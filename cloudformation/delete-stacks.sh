#!/bin/sh
set -eu

aws_profile="$1"
data_bucket="coffeetl-project-raw-data"
stack_name="coffeetl-project-etl-stack"
bucket="coffeetl-project-deployment-bucket"
deployment_stack="coffeetl-project-deployment-bucket"

# Check that we're logged in on this profile.
account_code=$(aws sts get-caller-identity --query "Account" --profile ${aws_profile})
# Re-log if our session expired.
if [ ${#account_code} -eq 14 ];  then 
    echo "Profile session still valid, skipping login."
else 
    aws sso login --profile ${aws_profile}
fi

{
    printf "\nEmptying ${data_bucket}...\n"
    aws s3 rm s3://${data_bucket} --recursive \
        --region eu-west-1 --profile ${aws_profile}
    printf "\nDeleting ${stack_name}...\n"
    aws cloudformation delete-stack --stack-name ${stack_name} \
        --region eu-west-1 --profile ${aws_profile}
} &
{
    printf "\nEmptying ${bucket}...\n"
    aws s3 rm s3://${bucket} --recursive \
        --region eu-west-1 --profile ${aws_profile}
    printf "\nDeleting ${deployment_stack}...\n"
    aws cloudformation delete-stack --stack-name ${deployment_stack} \
        --region eu-west-1 --profile ${aws_profile}
} &
printf "\nWaiting for jobs to finish...\n"
jobs
wait $(jobs -p)
