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
