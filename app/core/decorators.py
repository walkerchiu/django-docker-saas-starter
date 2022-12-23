def strip_input(func):
    def wrapped(info, *args, **input):
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

        result = func(info, *args, **input)

        return result

    return wrapped
