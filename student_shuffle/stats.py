from collections import defaultdict
from itertools import combinations


def pair_key(student_a, student_b):
    return "|".join(sorted((student_a, student_b)))


def partnership_score(group, pair_counts):
    return sum(
        pair_counts.get(pair_key(student_a, student_b), 0)
        for student_a, student_b in combinations(group, 2)
    )


def grade_counts(history):
    grades = defaultdict(int)
    for session in history.sessions:
        for student in session.graded:
            grades[student] += 1
    return grades


def pair_counts(history):
    counts = defaultdict(int)
    for session in history.sessions:
        groups = []
        if session.graded:
            groups.append(session.graded)
        groups.extend(session.practice)
        for group in groups:
            for student_a, student_b in combinations(group, 2):
                counts[pair_key(student_a, student_b)] += 1
    return counts
