import random
from .generate_resolution import generate_resolution

browser_types = ["browser", "mobile_browser"]
browser_names = ["Firefox", "Chrome", "Safari", "Edge", "Opera", "Internet Explorer"]
browser_versions = ["50.0", "60.0", "70.0", "80.0", "90.0", "100.0"]
browser_languages = ["en-US", "en-GB", "fr-FR", "es-ES", "de-DE", "ja-JP"]


# Generate 15 fake browser information
def generate_app():
    # Choose random values for each field
    browser_type = random.choice(browser_types)
    browser_name = random.choice(browser_names)
    browser_version = random.choice(browser_versions)
    browser_language = random.choice(browser_languages)

    # Construct the browser information dictionary
    browser_info = {
        "type": browser_type,
        "name": browser_name,
        "version": browser_version,
        "language": browser_language,
        "bot": False,
        "resolution": generate_resolution()
    }

    return browser_info
