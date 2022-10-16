def strip_dict(input: dict) -> dict:
    for key, item in input.items():
        if isinstance(item, str):
            input[key] = item.strip()
        elif isinstance(item, list):
            new = []
            for value in item:
                if isinstance(value, str):
                    new.append(value.strip())
                else:
                    new.append(value)
            input[key] = new
        else:
            input[key] = item

    return input
