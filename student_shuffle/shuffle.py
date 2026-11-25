import random
from collections import defaultdict
from itertools import combinations

from ortools.sat.python import cp_model


def shuffle_groups(
    students,
    partnership_score_function,
    grade_score_function,
    use_grade_group,
    use_practice_groups,
    graded_group_size,
    practice_group_size,
):
    students = students.copy()
    random.shuffle(students)

    graded_group = ()
    remaining_students = list(students)
    practice_groups = []

    if use_grade_group:
        grade_score_dict = defaultdict(list)
        for student in students:
            grade_score = grade_score_function(student)
            grade_score_dict[grade_score].append(student)

        mandatory_members = []
        current_tier_candidates = []

        for grade_score in sorted(grade_score_dict.keys()):
            tier_students = grade_score_dict[grade_score]
            if len(mandatory_members) + len(tier_students) < graded_group_size:
                mandatory_members.extend(tier_students)
            else:
                current_tier_candidates = tier_students
                break

        needed = graded_group_size - len(mandatory_members)

        if needed == 0:
            graded_group = tuple(mandatory_members)
        else:
            best_group = None
            min_score = float("inf")

            for sub in combinations(current_tier_candidates, needed):
                candidate_group = tuple(sorted(list(mandatory_members) + list(sub)))
                score = partnership_score_function(candidate_group)
                if score < min_score:
                    min_score = score
                    best_group = candidate_group

            graded_group = best_group

        remaining_students = [s for s in students if s not in graded_group]

    if use_practice_groups:
        model = cp_model.CpModel()
        num_remaining = len(remaining_students)

        candidate_groups = []
        group_scores = []

        for size in [2, 3]:
            for group in combinations(remaining_students, size):
                candidate_groups.append(group)
                group_scores.append(partnership_score_function(group))

        x = {}
        for i in range(len(candidate_groups)):
            x[i] = model.NewBoolVar(f"group_{i}")

        for student in remaining_students:
            relevant_indices = [i for i, group in enumerate(candidate_groups) if student in group]
            model.Add(sum(x[i] for i in relevant_indices) == 1)

        pair_indices = [i for i, group in enumerate(candidate_groups) if len(group) == 2]
        triad_indices = [i for i, group in enumerate(candidate_groups) if len(group) == 3]

        if practice_group_size == 2:
            if num_remaining % 2 == 0:
                model.Add(sum(x[i] for i in triad_indices) == 0)
            else:
                model.Add(sum(x[i] for i in triad_indices) == 1)
        elif practice_group_size == 3:
            remainder = num_remaining % 3
            if remainder == 0:
                model.Add(sum(x[i] for i in pair_indices) == 0)
            elif remainder == 1:
                model.Add(sum(x[i] for i in pair_indices) == 2)
            elif remainder == 2:
                model.Add(sum(x[i] for i in pair_indices) == 1)

        model.Minimize(sum(x[i] * group_scores[i] for i in range(len(candidate_groups))))

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for i in range(len(candidate_groups)):
                if solver.Value(x[i]) == 1:
                    practice_groups.append(candidate_groups[i])
        else:
            raise ValueError("No feasible grouping solution found for remaining students with given constraints.")

    return graded_group, practice_groups
