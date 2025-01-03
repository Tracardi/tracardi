def parse_accept_language(accept_language_header):
    parsed_languages = []
    if accept_language_header:
        # Remove any whitespace and split the header into individual language tags
        language_tags = accept_language_header.replace(" ", "").split(",")

        # Parse each language tag and extract the language and quality values
        for tag in language_tags:
            parts = tag.split(";")
            language = parts[0]
            quality = 1.0  # Default quality value is 1.0

            # Extract the quality value if present
            for part in parts[1:]:
                if part.startswith("q="):
                    quality = float(part[2:])

            if quality > 1:
                quality = 1

            if quality < 0:
                quality = 0

            parsed_languages.append((language, quality))

    return parsed_languages
