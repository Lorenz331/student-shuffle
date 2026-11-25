from datetime import date

from student_shuffle.cli.display import (
    clear,
    print_header,
    print_session,
    print_session_list,
    print_students,
)
from student_shuffle.cli.prompts import (
    ask_choice,
    ask_indices,
    ask_yes_no,
    parse_indices,
    parse_named_groups,
    pause,
)
from student_shuffle.models import History, Session
from student_shuffle.persistence import save_history
from student_shuffle.stats import grade_counts


def view_session(history: History) -> None:
    if not history.sessions:
        print("There are no sessions to view.")
        return

    indices = ask_indices(
        "Enter session id (or Enter to cancel): ",
        len(history.sessions),
        allow_empty=True,
    )
    if len(indices) != 1:
        if indices:
            print("Please enter a single session id.")
        else:
            print("Cancelled.")
        return

    session_id = indices[0]
    clear()
    print_header(f"MAIN > MANAGE SESSIONS > SESSION #{session_id + 1}")
    session = history.sessions[session_id]
    print_session(session.graded, session.practice)
    print(" Actions:")
    print("  [D] Delete Session")
    print("  [B] Back to Last Screen")
    print()
    option = ask_choice(
        "Select an option [B]: ",
        ["D", "B"],
        default="B",
    )
    if option != "D":
        return
    if not ask_yes_no("Delete this session?", default=False):
        print("Cancelled.")
        return
    history.sessions.pop(session_id)
    save_history(history)
    print("Session has been deleted.")


def manually_log(history: History) -> None:
    if len(history.students) < 2:
        print("Add at least two students before logging a session.")
        return

    clear()
    print_header("MAIN > MANAGE SESSIONS > LOG MANUALLY")
    print_students(history.students, grade_counts(history))

    graded = ()
    if ask_yes_no("Was one group graded today?", default=True):
        while True:
            raw = input(
                "Enter graded group student numbers separated by spaces (or Enter to cancel): "
            ).strip()
            if not raw:
                print("Cancelled.")
                return
            indices, error = parse_indices(raw, len(history.students))
            if error:
                print(error)
                continue
            if len(indices) not in (2, 3):
                print("The graded group must have 2 or 3 students.")
                continue
            graded = tuple(history.students[index] for index in indices)
            break

    practice = []
    if ask_yes_no("Did other students practice today?", default=True):
        while True:
            raw = input(
                "Enter practice groups; separate groups with commas and students with spaces (e.g. '1 2, 3 4 5'). Enter to cancel: "
            ).strip()
            if not raw:
                print("Cancelled.")
                return
            groups, error = parse_named_groups(raw, history.students)
            if error:
                print(error)
                continue
            practice = groups
            break

    if not graded and not practice:
        print("Error: A session needs a graded group or practice groups.")
        return

    seen = set()
    for group in [graded, *practice]:
        for student in group:
            if student in seen:
                print("Error: Students must not appear twice.")
                return
            seen.add(student)

    pause()
    clear()
    print_header("MAIN > MANAGE SESSIONS > LOG MANUALLY")
    print_session(graded, practice)
    if ask_yes_no("Confirm this session?", default=True):
        session = Session(
            date=date.today(),
            graded=graded,
            practice=practice,
        )
        history.sessions.append(session)
        save_history(history)
        print("Session recorded successfully!")
    else:
        print("Session discarded. Data was not saved.")


def manage_sessions(history: History) -> None:
    while True:
        clear()
        print_header(f"MAIN > MANAGE SESSIONS ({len(history.sessions)} Total)")
        print_session_list(history.sessions)
        print(" Actions:")
        print("  [V] View Session Details")
        print("  [M] Manually Log a Session")
        print("  [B] Back to Main Menu")
        print()
        option = ask_choice(
            "Select an action [B]: ",
            ["V", "M", "B"],
            default="B",
        )
        if option == "V":
            view_session(history)
        elif option == "M":
            manually_log(history)
        else:
            return
        pause()
