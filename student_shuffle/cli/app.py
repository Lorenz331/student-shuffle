from student_shuffle.cli.data_management import wipe_data
from student_shuffle.cli.display import WIDTH, clear, print_title_screen
from student_shuffle.cli.new_shuffle import new_shuffle
from student_shuffle.cli.prompts import ask_choice
from student_shuffle.cli.session_management import manage_sessions
from student_shuffle.cli.student_management import manage_students
from student_shuffle.persistence import load_history


def main() -> None:
    history = load_history()
    while True:
        clear()
        print_title_screen(len(history.students), len(history.sessions))
        print("    [1] New Shuffle")
        print("    [2] Manage Students")
        print("    [3] Manage Sessions")
        print("    [4] Reset")
        print("    [0] Exit")
        print("-" * WIDTH)
        option = ask_choice(
            "Select an option [1]: ",
            ["0", "1", "2", "3", "4"],
            default="1",
        )
        if option == "0":
            return
        if option == "1":
            new_shuffle(history)
        elif option == "2":
            manage_students(history)
        elif option == "3":
            manage_sessions(history)
        elif option == "4":
            wipe_data(history)
