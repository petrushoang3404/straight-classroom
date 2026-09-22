"""One-off helper to create (or reset the password of) a login user.

There's no sign-up flow in the app, so the first account has to be created
this way. Usage: `make be-seed-user u=admin p=secret d="Admin"`.
"""

import argparse

from sqlmodel import Session

# Importing the other model modules registers their tables on SQLModel's
# metadata; without this, resolving User.teacher_id's foreign key (and
# Teacher's relationships) fails since this script never loads them
# otherwise (see backend/alembic/env.py for the same requirement).
import backend.models.classroom_teachers  # noqa: F401
import backend.models.classrooms  # noqa: F401
import backend.models.students  # noqa: F401
import backend.models.teachers  # noqa: F401
from backend.models.users import User
from backend.repository.database import engine
from backend.repository.users import UserRepo
from backend.security import hash_password


def main():
    parser = argparse.ArgumentParser(description="Create or update a login user")
    parser.add_argument("--username", "-u", required=True)
    parser.add_argument("--password", "-p", required=True)
    parser.add_argument("--display-name", "-d", default="")
    parser.add_argument("--role", choices=["admin", "teacher"], default="admin")
    parser.add_argument(
        "--teacher-id",
        type=int,
        default=None,
        help="Teacher record to link this account to (required for role=teacher "
        "to have any classroom/student access)",
    )
    args = parser.parse_args()

    with Session(engine) as session:
        repo = UserRepo(session=session)
        user = repo.get_by_username(args.username)
        hashed_password = hash_password(args.password)

        if user is not None:
            user.hashed_password = hashed_password
            if args.display_name:
                user.display_name = args.display_name
            user.role = args.role
            user.teacher_id = args.teacher_id
            session.add(user)
            session.commit()
            print(f"Updated password for existing user '{args.username}'.")
        else:
            session.add(
                User(
                    username=args.username,
                    hashed_password=hashed_password,
                    display_name=args.display_name or args.username,
                    role=args.role,
                    teacher_id=args.teacher_id,
                )
            )
            session.commit()
            print(f"Created user '{args.username}'.")


if __name__ == "__main__":
    main()
