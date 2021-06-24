def search(query, groups):
    print(groups)
    for group in groups:
        if query in group.lower():
            return True
    return False
