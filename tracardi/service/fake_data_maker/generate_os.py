import random

# Define lists of possible values for the operating system name and version
os_names = ["Windows", "macOS", "Ubuntu", "Fedora", "Debian", "Arch Linux"]
os_versions = ["XP", "Vista", "7", "8", "10", "Mojave", "Catalina", "Big Sur", "20.04", "20.10", "21.04"]


def generate_os():
    # Generate a fake operating system name and version
    os_name = random.choice(os_names)
    os_version = random.choice(os_versions)

    # Construct the operating system information dictionary
    os_info = {
        "name": os_name,
        "version": os_version
    }

    # Construct the complete OS dictionary
    return os_info
