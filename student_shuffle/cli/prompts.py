def pause(message="Press ENTER to continue..."):
    input(message)


def ask_choice(prompt: str, options: list[str], default=None) -> str:
    allowed = {option.lower(): option for option in options}
    default_key = default.lower() if default is not None else None

    while True:
        raw = input(prompt).strip()
        if not raw:
            if default_key is not None:
                return allowed[default_key]
            print("Please select an option.")
            continue

        key = raw.lower()
        if key in allowed:
            return allowed[key]

        print("Invalid option. Please try again.")


def ask_yes_no(prompt: str, default=True) -> bool:
    suffix = " (Y/n): " if default else " (y/N): "
    while True:
        raw = input(prompt + suffix).strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please enter y or n.")


def ask_int_in(prompt: str, allowed: list[int]) -> int:
    allowed_list = list(allowed)
    allowed_set = set(allowed_list)
    choices = ", ".join(str(value) for value in allowed_list)

    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"Please enter a valid number ({choices}).")
            continue
        if value in allowed_set:
            return value
        print(f"Please enter {choices}.")


def parse_indices(text: str, count: int) -> tuple[list[int], str | None]:
    text = text.strip()
    if not text:
        return [], None
    if count <= 0:
        return [], "There are no items to select."

    indices = []
    seen = set()
    for part in text.split():
        try:
            number = int(part)
        except ValueError:
            return [], f"'{part}' is not a number."
        if number < 1 or number > count:
            return [], f"{number} is out of range (1-{count})."
        index = number - 1
        if index in seen:
            return [], f"Number {number} was entered more than once."
        seen.add(index)
        indices.append(index)
    return indices, None


def ask_indices(prompt: str, count: int, allow_empty=True) -> list[int]:
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_empty:
                return []
            print("Please enter at least one number, or leave empty to cancel.")
            continue
        indices, error = parse_indices(raw, count)
        if error:
            print(error)
            continue
        return indices


def parse_named_groups(text: str, students: list[str]) -> tuple[list[tuple[str, ...]], str | None]:
    chunks = [chunk.strip() for chunk in text.split(",") if chunk.strip()]
    if not chunks:
        return [], "Please enter at least one group."

    groups = []
    for chunk in chunks:
        indices, error = parse_indices(chunk, len(students))
        if error:
            return [], error
        if len(indices) < 2 or len(indices) > 3:
            return [], "Each group must have 2 or 3 students."
        groups.append(tuple(students[index] for index in indices))
    return groups, None
