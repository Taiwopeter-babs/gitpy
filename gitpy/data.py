#!/usr/bin/env python3
"""
Data module for gitpy
"""
import hashlib
import os
from typing import Tuple
import zlib
import sys


class GitpyData:

    GITPY_DIR = ".gitpy"
    __GITPY_OBJECTS_DATABASE = ".gitpy/objects"
    MODES = ["commit", "blob", "size"]
    OBJECT_TYPES = MODES[0:2] + ["tree"]

    def __init__(self) -> None:
        pass

    @staticmethod
    def write_file(path: str, data: bytes) -> None:
        """Write bytes of data to a file at a given path"""
        with open(path, "wb") as file:
            file.write(data)

    @staticmethod
    def read_file(path: str) -> bytes:
        """Read the bytes of data in a file at a given path"""
        with open(path, "rb") as file:
            return file.read()

    @staticmethod
    def init() -> Tuple[bool, str]:
        """
        Creates an empty `.gitpy` folder if it doesn't already exist
        """
        current_directory = os.getcwd()
        try:
            os.makedirs(GitpyData.GITPY_DIR, exist_ok=False)

            # objects database directory
            os.makedirs("{}".format(GitpyData.__GITPY_OBJECTS_DATABASE), exist_ok=False)

            return True, current_directory
        except FileExistsError:
            return False, current_directory

    @staticmethod
    def hash_object(data: bytes, obj_type: str, write=True) -> str:
        """
        Create a hash of object `data` with `header` + `NUL` + `data` concatenation
        - header: type of object and size in bytes
        - NUL: A binary `b''` format of NULL bytes

        Args:
            data: object data to be hashed
        Returns:
            A hash oof the `data`
        """

        assert (
            obj_type in GitpyData.OBJECT_TYPES
        ), "Object type not in accepted types {}".format(GitpyData.OBJECT_TYPES)

        header = "{} {}".format(obj_type, len(data)).encode()
        full_data = header + b"\x00" + data
        sha1 = hashlib.sha1(full_data).hexdigest()

        if write:
            """
            The path is constructed as .git/objects/ab/cd..
            ab: first two characters of the sha1
            cd: rest of the characters
            """
            path = os.path.join(GitpyData.__GITPY_OBJECTS_DATABASE, sha1[:2], sha1[2:])

            # compress data and save
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                GitpyData.write_file(path, zlib.compress(full_data))
        return sha1

    @staticmethod
    def cat_file(sha1_prefix: str, mode="blob") -> None:
        """
        Writes the content or information of an object to the stdout depending on the
        argument or flag
        #### Flags:
        - -m | --mode: If the mode is `commit` or `blob`, print the raw bytes of the object, otherwise
                     if the mode is size, print the size of the object.
        - -p | --prefix: The SHA-1 hash of the object to display

        Args:
            mode: The mode of the object to print
            sha1_prefix: The SHA hash of the object from which the path and filename is extracted
        """
        if mode not in GitpyData.MODES:
            raise ValueError("Unexpected mode ({!r})".format(mode))

        obj_type, obj_data = GitpyData.read_object(sha1_prefix)

        # mode defaults to blob
        if mode != obj_type:
            raise ValueError(
                "Expected object type ({}), got ({})".format(obj_type, mode)
            )

        if mode in ["commit", "blob"]:

            sys.stdout.flush()
            sys.stdout.buffer.write(obj_data)

        elif mode == "size":
            print(len(obj_data))

    @staticmethod
    def read_object(sha1_prefix: str) -> Tuple[str, bytes]:
        """
        Read object with given SHA-1 `sha1_prefix`
        """
        obj_path = GitpyData.find_object(sha1_prefix)
        full_data = zlib.decompress(GitpyData.read_file(obj_path))

        # Extract the header: object type and length
        null_index = full_data.index(b"\x00")
        header = full_data[0:null_index]

        obj_type, str_size = header.decode().split()
        obj_size = int(str_size)
        data = full_data[null_index + 1 :]

        assert obj_size == len(data), "Expected size ({}), got ({}) bytes".format(
            obj_size, len(data)
        )

        return (obj_type, data)

    @staticmethod
    def find_object(sha1_prefix: str) -> str:
        """
        Find an object with a given `sha1_prefix` and return the path to the object
        in the object database. If there are multiple objects or no objects with the the
        same prefix, a ValueError is raised
        """
        if len(sha1_prefix) < 2:
            raise ValueError("sha1_prefix must be 2 or more characters")

        object_dir = os.path.join(GitpyData.__GITPY_OBJECTS_DATABASE, sha1_prefix[:2])
        rest = sha1_prefix[2:]

        # Get object whose filename begins with the rest variable. See `hash_object`
        objects = [name for name in os.listdir(object_dir) if name.startswith(rest)]

        if not objects:
            raise ValueError("Object ({!r}) not found".format(sha1_prefix))
        if len(objects) > 1:
            raise ValueError(
                "Multiple objects ({}) with sha1 prefix {!r} found",
                len(objects),
                sha1_prefix,
            )

        return os.path.join(object_dir, objects[0])
