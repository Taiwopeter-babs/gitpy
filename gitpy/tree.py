"""
Tree handler module
"""

import os
from typing import Dict, List, Tuple
from gitpy.data import GitpyData


class GitpyTree:
    """Tree class"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def write_tree(directory=".") -> str:
        """
        Stores the current working directory/tree in the object database in this manner:

        `obj_type, obj_sha1, obj_name`

        Example:

        `blob 674jjdh7r747747484jd file.txt`\n
        `tree 234jjdh7r747747484jd pic_files`
        """

        tree_entries: List[Tuple[str, str, str]] = []

        with os.scandir(directory) as dir:
            for entry in dir:

                entry_path = "{}/{}".format(directory, entry.name)
                if GitpyTree.__is_ignored(entry_path):
                    continue

                # save each file to the object database
                if entry.is_file(follow_symlinks=False):
                    obj_type, obj_data = "blob", GitpyData.read_file(entry_path)
                    # write file to object database
                    obj_sha1 = GitpyData.hash_object(obj_data, obj_type)

                # Recursively save files found in directory to the object database, then
                # get the sha1 of the directory itself to be saved
                elif entry.is_dir(follow_symlinks=False):
                    obj_type = "tree"
                    obj_sha1 = GitpyTree.write_tree(entry_path)

                tree_entries.append((entry.name, obj_sha1, obj_type))

        # create tree object and save to object database
        tree_to_save = "".join(
            "{} {} {}\n".format(obj_type, obj_sha1, obj_name)
            for obj_name, obj_sha1, obj_type in sorted(tree_entries)
        )
        # print(tree_to_save)

        return GitpyData.hash_object(tree_to_save.encode(), "tree")

    @staticmethod
    def _iter_tree_entries(sha1: str | None):
        """Generator function for iterating through a tree's entries"""
        if not sha1:
            return
        _, tree_object_data = GitpyData.read_object(sha1)

        for entry in tree_object_data.decode().splitlines():
            print(entry.split(" ", 2))
            obj_type, obj_sha1, obj_name = entry.split(" ", 2)
            yield obj_type, obj_sha1, obj_name

    @staticmethod
    def get_tree(sha1: str, base_path="") -> Dict[str, str]:
        """Recursively parse the contents of a tree into a dictionary"""
        parsed_result: Dict[str, str] = {}

        for obj_type, obj_sha1, obj_name in GitpyTree._iter_tree_entries(sha1):

            if obj_type not in GitpyData.OBJECT_TYPES:
                assert ValueError, "Unknown tree entry {}".format(obj_type)

            # directories/trees names must be pure
            assert "/" not in obj_name
            assert obj_name not in ("..", ".")

            obj_path = base_path + obj_name

            if obj_type == "blob":
                parsed_result[obj_path] = obj_sha1
            elif obj_type == "tree":
                parsed_result.update(
                    GitpyTree.get_tree(obj_sha1, "{}/".format(obj_path))
                )

        return parsed_result

    @staticmethod
    def read_tree(tree_sha1):
        """Gets the content of a tree object and write them into the working directory"""
        # empty directory
        GitpyTree.__empty_current_directory()
        for obj_path, obj_sha1 in GitpyTree.get_tree(tree_sha1, base_path="./").items():
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)
            GitpyData.write_file(obj_path, GitpyData.read_object(obj_sha1)[1])

    @staticmethod
    def commit(message: str):
        """
        Creates a new commit object and saves to the object database.
        The first lines will be key-values. An empty line marks the end of the key-values, then
        the commit message.

        The key-values:
        - `obj_type obj_sha1`
        - `author name`
        - `time YYYY-MM-DDTHH:MM:SS`
        """
        commit = "{} {}\n".format("tree", GitpyTree.write_tree())
        commit += "\n{}\n".format(message)

        return GitpyData.hash_object(commit.encode(), "commit")

    @staticmethod
    def __empty_current_directory():
        """Delete the current directory with files and subdirectories within"""
        for dirpath, dirnames, filenames in os.walk(".", topdown=False):

            # remove files in the directory
            for filename in filenames:
                # print(dirpath, filename)
                path = os.path.relpath("{}/{}".format(dirpath, filename))
                # print(path)
                if GitpyTree.__is_ignored(path) or not os.path.isfile(path):
                    continue
                os.remove(path)

            # remove directories
            for dirname in dirnames:
                path = os.path.relpath("{}/{}".format(dirpath, dirname))
                if GitpyTree.__is_ignored(path) or os.path.isfile(path):
                    continue
                try:
                    os.rmdir(path)
                except (OSError, FileNotFoundError):
                    pass

    @staticmethod
    def __is_ignored(path: str) -> bool:
        """Checks if a file or directory is ignored"""
        to_be_ignored = [GitpyData.GITPY_DIR, "gitpyvenv", ".git"]
        ignored = any(map(lambda p: p in path.split("/"), to_be_ignored))

        return ignored
