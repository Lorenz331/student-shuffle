from student_shuffle.cli.display import WIDTH, clear, print_counts, print_header
from student_shuffle.cli.prompts import ask_choice, ask_yes_no, pause
from student_shuffle.models import History
from student_shuffle.persistence import save_history


def wipe_data(history: History) -> None:
    clear()
    print_header("MAIN > RESET & DATA MANAGEMENT")
    print_counts(len(history.students), len(history.sessions))
    print("-" * WIDTH)
    print("  [1] Clear Session History")
    print("  [2] Clear Everything")
    print("  [B] Back to Main Menu")
    print()
    option = ask_choice(
        "Select an option [B]: ",
        ["1", "2", "B"],
        default="B",
    )
    if option == "1":
        if not ask_yes_no("Delete all session history?", default=False):
            print("Cancelled.")
            return
        history.sessions = []
        save_history(history)
        print("All sessions have been wiped.")
    elif option == "2":
        if not ask_yes_no("Delete all students and sessions?", default=False):
            print("Cancelled.")
            return
        history.students = []
        history.sessions = []
        save_history(history)
        print("All data has been wiped.")
    else:
        return
    pause("Press ENTER to return to main menu...")
