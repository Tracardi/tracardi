def search(query, groups):
    for group in groups:
        if query in group.lower():
            return True
    return False
