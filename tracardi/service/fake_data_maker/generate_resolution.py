import random

# Define a list of common aspect ratios
aspect_ratios = [(4, 3), (16, 9), (18, 9), (21, 9), (32, 9)]

# Define a list of common resolutions for each aspect ratio
resolutions = {
    (4, 3): [(800, 600), (1024, 768), (1280, 960), (1600, 1200)],
    (16, 9): [(1280, 720), (1366, 768), (1920, 1080), (2560, 1440)],
    (18, 9): [(1440, 720), (2160, 1080), (2880, 1440)],
    (21, 9): [(2560, 1080), (3440, 1440), (5120, 2160)],
    (32, 9): [(3840, 1080), (5120, 1440)]
}


def generate_resolution():
    # Generate 50 random screen resolutions
    for i in range(50):
        # Choose a random aspect ratio from the list
        aspect_ratio = random.choice(aspect_ratios)

        # Choose a random resolution for the chosen aspect ratio
        resolution = random.choice(resolutions[aspect_ratio])

        # Print the chosen resolution
        return f"{resolution[0]}x{resolution[1]}"
