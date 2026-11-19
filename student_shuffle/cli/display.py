import math
import os

WIDTH = 50


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    print("=" * WIDTH)
    print(f" {title}")
    print("=" * WIDTH)


def print_title_screen(student_count, session_count):
    print("=" * WIDTH)
    print(f"{'STUDENT SHUFFLE':^{WIDTH}}")
    print(f"{'by Lorenz':^{WIDTH}}")
    print("=" * WIDTH)
    print_counts(student_count, session_count)
    print("-" * WIDTH)


def print_counts(student_count, session_count):
    left = f"{student_count} Students"
    right = f"{session_count} Sessions"
    print(f"{left:^24} | {right:^24}")


def print_students(students, grades):
    if not students:
        print("  No students yet.")
        print("-" * WIDTH)
        return

    print("  #  Name                  Grades  |  #  Name                  Grades")
    print("-----------------------------------+----------------------------------")
    left_length = math.ceil(len(students) / 2)
    for i in range(left_length):
        line = f" {(i + 1):2d}. {students[i]:<20} {grades[students[i]]:2d}       |"
        j = left_length + i
        if j < len(students):
            line += f" {(j + 1):2d}. {students[j]:<20} {grades[students[j]]:2d}"
        print(line)
    print("-----------------------------------+----------------------------------")


def print_session(graded, practice):
    if graded:
        print(f"Graded Group:\n - {', '.join(graded)}")
    if practice:
        if graded:
            print()
        print("Practice Groups:")
        for group in practice:
            print(f" - {', '.join(group)}")
    print("-" * WIDTH)


def print_session_list(sessions):
    print("  ID   Date        Graded                                   Practice")
    print("-" * 70)
    if not sessions:
        print("  No sessions yet.")
    else:
        for i, session in enumerate(sessions, 1):
            graded = ", ".join(session.graded) if session.graded else "-"
            if len(graded) > 40:
                graded = graded[:37] + "..."
            practice_count = len(session.practice)
            practice_students = sum(len(group) for group in session.practice)
            print(f"  #{i:<3} {session.date.strftime('%d.%m.%Y'):<11} {graded:<40} {practice_count}g/{practice_students}s")
    print("-" * 70)
