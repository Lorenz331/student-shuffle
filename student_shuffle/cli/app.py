from datetime import date

from student_shuffle.cli.display import (
    WIDTH,
    clear,
    print_counts,
    print_header,
    print_session,
    print_session_list,
    print_students,
    print_title_screen
)
from student_shuffle.cli.prompts import (
    ask_choice,
    ask_indices,
    ask_int_in,
    ask_yes_no,
    parse_indices,
    parse_named_groups,
    pause
)
from student_shuffle.models import Session
from student_shuffle.persistence import load_history, save_history
from student_shuffle.shuffle import shuffle_groups
from student_shuffle.stats import grade_counts, pair_counts, partnership_score


class CLI:
    def __init__(self):
        self.history = load_history()

    def run(self):
        try:
            while self.main_menu():
                pass
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")

    def save(self):
        save_history(self.history)

    def main_menu(self):
        try:
            clear()
            print_title_screen(len(self.history.students), len(self.history.sessions))
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
                return False
            if option == "1":
                self.new_shuffle()
            elif option == "2":
                self.manage_students()
            elif option == "3":
                self.manage_sessions()
            elif option == "4":
                self.wipe_data()
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as error:
            print(f"\nError: {error}")
            pause()
        return True

    def new_shuffle(self):
        clear()
        print_header("MAIN > NEW SHUFFLE > STEP 1: ABSENCE")

        if len(self.history.students) < 2:
            print("Not enough students to form groups. Add students first.")
            pause("Press ENTER to return to main menu...")
            return

        grades = grade_counts(self.history)
        pairs = pair_counts(self.history)
        print_students(self.history.students, grades)

        absent_indices = ask_indices(
            "Enter absent student numbers separated by spaces: ",
            len(self.history.students),
            allow_empty=True,
        )
        absent = set(absent_indices)
        active_students = [
            student
            for index, student in enumerate(self.history.students)
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
            self.history.sessions.append(session)
            self.save()
            print("Session recorded successfully!")
            break

        pause("Press ENTER to return to main menu...")

    def manage_students(self):
        while True:
            clear()
            print_header(f"MAIN > MANAGE STUDENTS ({len(self.history.students)} Total)")
            print_students(self.history.students, grade_counts(self.history))
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
                self._add_students()
            elif option == "R":
                self._remove_students()
            else:
                return
            pause()

    def _add_students(self):
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

        existing_lookup = {student.lower(): student for student in self.history.students}
        existing_names = []
        new_names = []
        for name in names:
            if name.lower() in existing_lookup:
                existing_names.append(existing_lookup[name.lower()])
            else:
                new_names.append(name)

        self.history.students.extend(new_names)
        self.history.students.sort()
        self.save()
        if existing_names:
            print(f"Already existed: {', '.join(existing_names)}")
        if new_names:
            print(f"Added: {', '.join(new_names)}")

    def _remove_students(self):
        if not self.history.students:
            print("There are no students to remove.")
            return

        indices = ask_indices(
            "Enter number(s) separated by spaces (or Enter to cancel): ",
            len(self.history.students),
            allow_empty=True,
        )
        if not indices:
            print("Cancelled.")
            return

        removed = [self.history.students[index] for index in sorted(indices)]
        for index in sorted(indices, reverse=True):
            self.history.students.pop(index)
        self.save()
        print(f"Removed: {', '.join(removed)}")

    def manage_sessions(self):
        while True:
            clear()
            print_header(f"MAIN > MANAGE SESSIONS ({len(self.history.sessions)} Total)")
            print_session_list(self.history.sessions)
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
                self._view_session()
            elif option == "M":
                self.manually_log()
            else:
                return
            pause()

    def _view_session(self):
        if not self.history.sessions:
            print("There are no sessions to view.")
            return

        indices = ask_indices(
            "Enter session id (or Enter to cancel): ",
            len(self.history.sessions),
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
        session = self.history.sessions[session_id]
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
        self.history.sessions.pop(session_id)
        self.save()
        print("Session has been deleted.")

    def manually_log(self):
        if len(self.history.students) < 2:
            print("Add at least two students before logging a session.")
            return

        clear()
        print_header("MAIN > MANAGE SESSIONS > LOG MANUALLY")
        print_students(self.history.students, grade_counts(self.history))

        graded = ()
        if ask_yes_no("Was one group graded today?", default=True):
            while True:
                raw = input("Enter graded group student numbers separated by spaces (or Enter to cancel): ").strip()
                if not raw:
                    print("Cancelled.")
                    return
                indices, error = parse_indices(raw, len(self.history.students))
                if error:
                    print(error)
                    continue
                if len(indices) not in (2, 3):
                    print("The graded group must have 2 or 3 students.")
                    continue
                graded = tuple(self.history.students[index] for index in indices)
                break

        practice = []
        if ask_yes_no("Did other students practice today?", default=True):
            while True:
                raw = input("Enter practice groups; separate groups with commas and students with spaces (e.g. '1 2, 3 4 5'). Enter to cancel: ").strip()
                if not raw:
                    print("Cancelled.")
                    return
                groups, error = parse_named_groups(raw, self.history.students)
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
            self.history.sessions.append(session)
            self.save()
            print("Session recorded successfully!")
        else:
            print("Session discarded. Data was not saved.")

    def wipe_data(self):
        clear()
        print_header("MAIN > RESET & DATA MANAGEMENT")
        print_counts(len(self.history.students), len(self.history.sessions))
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
            self.history.sessions = []
            self.save()
            print("All sessions have been wiped.")
        elif option == "2":
            if not ask_yes_no("Delete all students and sessions?", default=False):
                print("Cancelled.")
                return
            self.history.students = []
            self.history.sessions = []
            self.save()
            print("All data has been wiped.")
        else:
            return
        pause("Press ENTER to return to main menu...")


def main():
    CLI().run()
