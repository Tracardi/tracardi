def is_valid_string(variable):
    """
    Check if the variable is a string composed of alphanumeric characters, underscores (_), and hyphens (-),
    contains no spaces, and has at least one alphanumeric character.

    Args:
    variable (str): The variable to be checked.

    Returns:
    bool: True if the variable meets the criteria, False otherwise.
    """
    if not isinstance(variable, str):
        return False

    # Check for at least one alphanumeric character
    if not any(char.isalnum() for char in variable):
        return False

    # Checking if all characters are alphanumeric, underscore, or hyphen, and if there are no spaces
    return all(char.isalnum() or char in ['_', '-'] for char in variable) and ' ' not in variable

