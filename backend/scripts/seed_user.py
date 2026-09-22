"""One-off helper to create (or reset the password of) a login user.

There's no sign-up flow in the app, so the first account has to be created
this way. Usage: `make be-seed-user u=admin p=secret d="Admin"`.
"""

import argparse

from sqlmodel import Session

from backend.models.users import User
from backend.repository.database import engine
from backend.repository.users import UserRepo
from backend.security import hash_password


def main():
    parser = argparse.ArgumentParser(description="Create or update a login user")
    parser.add_argument("--username", "-u", required=True)
    parser.add_argument("--password", "-p", required=True)
    parser.add_argument("--display-name", "-d", default="")
    args = parser.parse_args()

    with Session(engine) as session:
        repo = UserRepo(session=session)
        user = repo.get_by_username(args.username)
        hashed_password = hash_password(args.password)

        if user is not None:
            user.hashed_password = hashed_password
            if args.display_name:
                user.display_name = args.display_name
            session.add(user)
            session.commit()
            print(f"Updated password for existing user '{args.username}'.")
        else:
            session.add(
                User(
                    username=args.username,
                    hashed_password=hashed_password,
                    display_name=args.display_name or args.username,
                )
            )
            session.commit()
            print(f"Created user '{args.username}'.")


if __name__ == "__main__":
    main()
