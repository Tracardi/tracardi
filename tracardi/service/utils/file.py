def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return content
