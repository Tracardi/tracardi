from datetime import timedelta


def pretty_time_format(time_in_seconds: float) -> str:
    hours = int(time_in_seconds // 3600)
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = int(time_in_seconds % 60)
    milliseconds = int((time_in_seconds % 1) * 1000)

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:05}"
    else:
        return f"{minutes:02}:{seconds:02}.{milliseconds:05}"

def pretty_ms_format(time_in_seconds: float) -> str:
    seconds = int(time_in_seconds % 60)
    milliseconds = int((time_in_seconds % 1) * 1000)

    return f"{seconds:02}.{milliseconds:05}"


def pretty_seconds(total_seconds):
    # Create a timedelta object
    td = timedelta(seconds=total_seconds)

    # Extract days, hours, minutes, and seconds
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Build a list of parts, only adding non-zero values (unless it's the only unit)
    parts = []
    if days > 0:
        parts.append(f"{days}")
    if hours > 0:
        parts.append(f"{hours}")
    if minutes > 0:
        parts.append(f"{minutes}")

    # Always show seconds
    parts.append(f"{seconds:02d}s")

    return ':'.join(parts)