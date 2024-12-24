"""Module defining one simple method to deduplicate elements of a list.
"""

def deduplicate(li: list) -> list:
    """Naively deduplicates elements of a list.

    Args:
        li (list): List which may contain duplicate items

    Returns:
        list: A list of the first unique instance of each elements of the
            input.
    """
    new = []
    for i in li:
        if i not in new:
            new.append(i)
    return new
