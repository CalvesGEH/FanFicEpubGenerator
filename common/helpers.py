def parse_fiction_ids_from_file(file) -> list[int]:
    """
    Parse fiction ids from a comma or a newline separated file.
    Returns empty list if the file is empty or can't be parsed.

    Args:
        file: A file object to read from.

    Returns:
        list[int]: A list of fiction ids. Returns empty list if the file is empty or can't be parsed. 
    """
    with open(file, 'r') as file:
        ids = []
        for line in file.readlines():
            ids.extend([int(fiction_id) for fiction_id in line.split(',')])
        return ids