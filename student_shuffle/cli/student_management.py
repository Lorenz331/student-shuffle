from student_shuffle.cli.display import clear, print_header, print_students
from student_shuffle.cli.prompts import ask_choice, ask_indices, pause
from student_shuffle.models import History
from student_shuffle.persistence import save_history
from student_shuffle.stats import grade_counts


def add_students(history: History) -> None:
    raw = input("Enter student name(s) separated by commas: ")
    names = []
    seen = set()
    for name in raw.split(","):
        name = name.strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        names.append(name)

    if not names:
        print("No names entered.")
        return

    existing_lookup = {student.lower(): student for student in history.students}
    existing_names = []
    new_names = []
    for name in names:
        if name.lower() in existing_lookup:
            existing_names.append(existing_lookup[name.lower()])
        else:
            new_names.append(name)

    history.students.extend(new_names)
    history.students.sort()
    save_history(history)
    if existing_names:
        print(f"Already existed: {', '.join(existing_names)}")
    if new_names:
        print(f"Added: {', '.join(new_names)}")


def remove_students(history: History) -> None:
    if not history.students:
        print("There are no students to remove.")
        return

    indices = ask_indices(
        "Enter number(s) separated by spaces (or Enter to cancel): ",
        len(history.students),
        allow_empty=True,
    )
    if not indices:
        print("Cancelled.")
        return

    removed = [history.students[index] for index in sorted(indices)]
    for index in sorted(indices, reverse=True):
        history.students.pop(index)
    save_history(history)
    print(f"Removed: {', '.join(removed)}")


def manage_students(history: History) -> None:
    while True:
        clear()
        print_header(f"MAIN > MANAGE STUDENTS ({len(history.students)} Total)")
        print_students(history.students, grade_counts(history))
        print(" Actions:")
        print("  [A] Add Student(s)")
        print("  [R] Remove Student(s)")
        print("  [B] Back to Main Menu")
        print()
        option = ask_choice(
            "Select an action [B]: ",
            ["A", "R", "B"],
            default="B",
        )
        if option == "A":
            add_students(history)
        elif option == "R":
            remove_students(history)
        else:
            return
        pause()
