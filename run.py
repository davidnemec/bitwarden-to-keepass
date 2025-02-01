import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from getpass import getpass
from pathlib import Path

from src.bitwarden_to_keepass import bitwarden_to_keepass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def check_args(args: Namespace) -> Namespace:
    if not args.database_password:
        args.database_password = getpass(
            "Enter the database password (will not display): ",
        )

    if not args.database_password:
        raise RuntimeError("A database password must be supplied.")

    if args.database_keyfile and (
        not Path(args.database_keyfile).is_file()
        or not os.access(
            args.database_keyfile,
            os.R_OK,
        )
    ):
        raise RuntimeError("Key File for KeePass database is not readable.")

    if not Path(args.bw_path).is_file() or not os.access(args.bw_path, os.X_OK):
        raise RuntimeError(
            "bitwarden-cli was not found or not executable. "
            "Did you set correct '--bw-path'?",
        )

    return args


def environ_or_required(key: str) -> dict:
    return (
        {"default": os.environ.get(key)} if os.environ.get(key) else {"required": True}
    )


parser = ArgumentParser()
parser.add_argument(
    "--bw-session",
    help="Session generated from bitwarden-cli (bw login)",
    **environ_or_required("BW_SESSION"),
)
parser.add_argument(
    "--database-path",
    help="Path to KeePass database. If database does not exists it will be created.",
    **environ_or_required("DATABASE_PATH"),
)
parser.add_argument(
    "--database-password",
    help="Password for KeePass database",
    default=os.environ.get("DATABASE_PASSWORD", None),
)
parser.add_argument(
    "--database-keyfile",
    help="Path to Key File for KeePass database",
    default=os.environ.get("DATABASE_KEYFILE", None),
)
parser.add_argument(
    "--bw-path",
    help="Path for bw binary",
    default=os.environ.get("BW_PATH", "bw"),
)
args = parser.parse_args()

try:
    check_args(args)
    bitwarden_to_keepass(args)
except RuntimeError:
    logging.exception("Exception occurred.")
    sys.exit(1)
