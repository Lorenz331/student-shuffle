from datetime import date

from student_shuffle.cli.display import (
    clear,
    print_header,
    print_session,
    print_students,
)
from student_shuffle.cli.prompts import (
    ask_choice,
    ask_indices,
    ask_int_in,
    ask_yes_no,
    pause,
)
from student_shuffle.models import History, Session
from student_shuffle.persistence import save_history
from student_shuffle.shuffle import shuffle_groups
from student_shuffle.stats import grade_counts, pair_counts, partnership_score


def new_shuffle(history: History) -> None:
    clear()
    print_header("MAIN > NEW SHUFFLE > STEP 1: ABSENCE")

    if len(history.students) < 2:
        print("Not enough students to form groups. Add students first.")
        pause("Press ENTER to return to main menu...")
        return

    grades = grade_counts(history)
    pairs = pair_counts(history)
    print_students(history.students, grades)

    absent_indices = ask_indices(
        "Enter absent student numbers separated by spaces: ",
        len(history.students),
        allow_empty=True,
    )
    absent = set(absent_indices)
    active_students = [
        student
        for index, student in enumerate(history.students)
        if index not in absent
    ]
    print(f"{len(active_students)} active students today.")
    if len(active_students) < 2:
        print("Error: Not enough active students to form groups.")
        pause("Press ENTER to return to main menu...")
        return
    pause()

    clear()
    print_header("MAIN > NEW SHUFFLE > STEP 2: OPTIONS")
    grade_today = ask_yes_no("Grade one group today?", default=True)
    grade_group_size = 0
    if grade_today:
        while True:
            grade_group_size = ask_int_in(
                "Enter size of the graded group (2 or 3): ",
                [2, 3],
            )
            if grade_group_size is None:
                print("Cancelled.")
                pause("Press ENTER to return to main menu...")
                return
            if len(active_students) < grade_group_size:
                print("Not enough active students for that group size.")
                continue
            break

    if len(active_students) - grade_group_size >= 2:
        practice_today = ask_yes_no(
            "Let other students practice today?",
            default=True,
        )
    else:
        practice_today = False

    practice_group_size = 0
    if practice_today:
        practice_group_size = ask_int_in(
            "Enter size of the practice groups (2 or 3): ",
            [2, 3],
        )
        if practice_group_size is None:
            print("Cancelled.")
            pause("Press ENTER to return to main menu...")
            return

    if not grade_today and not practice_today:
        print("Error: A session needs a graded group or practice groups.")
        pause("Press ENTER to return to main menu...")
        return

    pause()

    while True:
        try:
            graded_group, practice_groups = shuffle_groups(
                active_students,
                lambda group: partnership_score(group, pairs),
                lambda student: grades.get(student, 0),
                grade_today,
                practice_today,
                grade_group_size,
                practice_group_size,
            )
        except ValueError as error:
            print(f"\nError: {error}")
            pause("Press ENTER to return to main menu...")
            return

        clear()
        print_header("MAIN > NEW SHUFFLE > STEP 3: REVIEW AND SAVE")
        print_session(graded_group, practice_groups)
        print(" Actions:")
        print("  [S] Save Session")
        print("  [R] Re-shuffle Groups")
        print("  [D] Discard Session")
        print()
        option = ask_choice(
            "Select an option [S]: ",
            ["S", "R", "D"],
            default="S",
        )
        if option == "D":
            print("Session discarded. Data was not saved.")
            break
        if option == "R":
            continue

        session = Session(
            date=date.today(),
            graded=graded_group,
            practice=practice_groups,
        )
        history.sessions.append(session)
        save_history(history)
        print("Session recorded successfully!")
        break

    pause("Press ENTER to return to main menu...")
