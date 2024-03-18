#!/usr/bin/env python3
"""
Module that processes the pygit commands
"""
from argparse import Namespace, ArgumentParser
import sys
from gitpy import gitpy_data

INIT_HELP = "Initialize a new gitpy repo"
HASH_OBJECT_HELP = "Saves the content of a file to the objects database"
CAT_FILE_HELP = """
Logs the content of the object to stdout.

gitpy cat-file [-m] -p hash-prefix object
"""


def parse_args() -> Namespace:
    """The command line arguments parser"""
    parser = ArgumentParser()

    # command line arguments
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    # gitpy init
    init_parser = commands.add_parser("init", help=INIT_HELP)
    init_parser.set_defaults(func=init)

    # gitpy hash_object
    hash_object_parser = commands.add_parser("hash-object", help=HASH_OBJECT_HELP)
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")

    # gitpy cat-file
    cat_file_parser = commands.add_parser("cat-file", help=CAT_FILE_HELP)
    valid_modes = gitpy_data.MODES
    cat_file_parser.add_argument(
        "-m", "--mode", choices=valid_modes, help="Information to print"
    )
    # cat_file_parser.add_argument(
    #     "-p",
    #     "--prefix",
    #     required=True,
    #     help="SHA-1 hash (or hash prefix) of object to display",
    # )
    cat_file_parser.add_argument(
        "object",
        help="SHA-1 hash (or hash prefix) of object to display",
    )
    cat_file_parser.set_defaults(func=cat_file)

    return parser.parse_args()


def init(args) -> None:
    """Intializes a new repository by creating a `.gitpy` folder"""
    is_init, current_directory = gitpy_data.init()
    if is_init:
        print(
            "Initialized empty gitpy repository in {}/{}".format(
                current_directory, gitpy_data.GITPY_DIR
            )
        )
    else:
        print("{} is already a gitpy repository".format(current_directory))


def hash_object(args):
    """Hashes the content of a file and saves to the objects database"""
    # print(args.file, type(args))
    file_content = gitpy_data.read_file(args.file)
    print(gitpy_data.hash_object(file_content, "blob"))


def cat_file(args):
    """Prints to the stdout the content or info of the object"""
    try:
        gitpy_data.cat_file(args.mode, args.object)
    except ValueError as error:
        sys.stdout.flush()
        sys.stdout.buffer.write("{}\n".format(str(error)).encode())


def main():
    args = parse_args()
    args.func(args)
