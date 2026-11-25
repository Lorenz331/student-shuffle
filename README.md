# Student Shuffle

A classroom helper I built for my teacher that builds graded and practice groups while trying to avoid repeating partnerships and spreading grades across students.

## How it works

- Students and past sessions are saved as `history.json` in the platform user data directory.

- Students with the least grades are getting graded before others.

- Pairs with a higher repitition get a worse score than pairs that worked together less often.

- The constallation with the best overall scores is chosen.

## Menus

- **New Shuffle**: Mark absences, choose graded/practice group sizes, review, save or re-shuffle.

- **Manage Students**: Add or remove names.

- **Manage Sessions**: View, delete, or manually log a session.

- **Reset**: Clear sessions or everything.

## How to Run

You need Python 3.13 and the packages in `requirements.txt`:

```
pip install -r requirements.txt
```

From the project root run:

```
python -m student_shuffle
```
