import os


def write_to_file():
    pass


def load(directory: str) -> list[str]:
    inputs = []
    inputs.extend(load_from_files(directory+ "/positive_inputs"))
    inputs.extend(load_from_files(directory + "/negative_inputs"))
    return inputs


def load_from_files(directory: str) -> list[str]:
    inputs = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                try:
                    inputs.append(content)
                except Exception as e:
                    print(f"Failed to load {filepath}: {e}")
    return inputs