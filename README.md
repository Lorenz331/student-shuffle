# Student Shuffle

A small classroom helper I built for my teacher that builds graded and practice groups while trying to avoid repeating partnerships and spreading grades across students.

## How it works

- Students and past sessions are saved as `history.json` in the platform user data directory.

- When the shuffle algorithm works, students with the least grades are getting graded before others.

- Pairs with a higher repitition get a worse score than pairs that worked together less often.

- The constallation with the best overall scores is chosen.

## Menus

- **New Shuffle**: mark absences, choose graded/practice group sizes, review, save or re-shuffle

- **Manage Students**: add or remove names

- **Manage Sessions**: view, delete, or manually log a session

- **Reset**: clear sessions or everything

## How to Run

You need Python 3.13 and the packages in `requirements.txt`:

```
pip install -r requirements.txt
```

From the project root run:

```
python -m student_shuffle
```
