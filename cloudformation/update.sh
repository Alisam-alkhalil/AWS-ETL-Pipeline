#!/bin/sh
set -eu

## Configs
aws_profile="$1"
deployment_bucket="coffeetl-project-deployment-bucket"
ec2_ingress_ip=$(curl api.ipify.org)  # This api just echos your ip.
ec2_userdata=$(base64 -i userdata)
## End configs

if [[ "$OSTYPE" == "msys" ]]; then
    # MINGW64 / git bash on windows
    pyver="py"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OSX I think, but can't check.
    pyver="python3"
else
    echo "Unexpected OSTYPE, this script is intended to be run in\
 Git Bash on Windows (msys), but OSTYPE is $OSTYPE."
    exit 1
fi

# Check that we're logged in on this profile.
account_code=$(aws sts get-caller-identity --query "Account" --profile ${aws_profile})
# Re-log if our session expired.
if [ ${#account_code} -eq 14 ];  then 
    echo "Profile session still valid, skipping login."
else 
    aws sso login --profile ${aws_profile}
fi

# I think this should be able to do something a little fancier with the pip
# install when it's skipped, but this works.
# TODO: Make this fancier, consider using 3rd directory to check if we have
#   the requirements installed already.
printf "\nDeleting old packagedsrc..."
rm -r ../packagedsrc
printf "\nMaking a copy of local code...\n"
cp -r ../src ../packagedsrc

if [ -z "${SKIP_PIP_INSTALL:-}" ]; then
    printf "\nDoing pip install.\n"
    $pyver -m pip install --platform manylinux2014_x86_64 \
        --target=../packagedsrc --implementation cp --python-version 3.13 \
        --only-binary=:all: --upgrade -q -r requirements-lambda.txt
else
    printf "\nSkipping pip install."
fi

# No wait because the deployment bucket should be already deployed.

printf "\nPackaging ETL pipeline stack..."
aws cloudformation package \
    --template-file etl-pipeline-stack.yml \
    --s3-bucket ${deployment_bucket} \
    --output-template-file etl-stack-packaged.yml \
    --profile ${aws_profile}

printf "\nUpdating remote ETL pipeline stack..."
aws cloudformation update-stack \
    --stack-name coffeetl-project-etl-stack \
    --template-body "file://etl-stack-packaged.yml" \
    --region eu-west-1 \
    --capabilities CAPABILITY_IAM \
    --profile ${aws_profile} \
    --parameters \
        EC2InstanceIngressIp="${ec2_ingress_ip}" \
        EC2UserData="${ec2_userdata}"

printf "\nDone."