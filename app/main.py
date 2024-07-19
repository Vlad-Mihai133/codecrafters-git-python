import sys
import os
import zlib
import hashlib


def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")


def cat_file(command):
    if len(sys.argv) != 4:
        print(f"Unknown command #{command}", file=sys.stderr)
    if sys.argv[2] == "-p":
        blob_sha = sys.argv[3]
        with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as file:
            raw = zlib.decompress(file.read())
            header, content = raw.split(b"\0", maxsplit=1)
            print(content.decode("utf-8"), end="")


def hash_object(command):
    """only made to work with -w when calling this function
    can be improved"""
    if sys.argv[2] != "-w":
        raise RuntimeError(f"Unknown command #{command}, use with -w")
    else:
        file_name = sys.argv[3]
    with open(file_name, "rb") as file:
        file_content = file.read()
    # get path
    git_path = os.path.join(os.getcwd(), ".git/objects")
    # make blob header
    obj_header = f"blob {len(file_content)}\x00"
    # this is blob header + content
    obj_content = obj_header.encode("ascii") + file_content
    # here we get the SHA hash
    sha = hashlib.sha1(obj_content).hexdigest()
    os.mkdir(os.path.join(git_path, sha[:2]))
    with open(os.path.join(git_path, sha[:2], sha[2:]), "wb") as file:
        file.write(zlib.compress(obj_content))
    print(sha, end='')


def ls_tree(command):
    """For example, if you had a directory structure like this:

  your_repo/
    - file1
    - dir1/
      - file_in_dir_1
      - file_in_dir_2
    - dir2/
      - file_in_dir_3
The entries in the tree object would look like this:

  040000 dir1 <tree_sha_1>
  040000 dir2 <tree_sha_2>
  100644 file1 <blob_sha_1>

  SOURCE: CodeCrafters: Build your own Git, stage 4 ("Read a tree object")
  link: https://app.codecrafters.io/courses/git/stages/kp1"""

    # here we check if the command is right
    if len(sys.argv) != 3 or len(sys.argv) != 4:
        raise RuntimeError(f"Unknown command #{command}")
    if sys.argv[2] == "--name-only":
        tree_hash = sys.argv[3]
    else:
        if len(sys.argv) == 4:
            raise RuntimeError(f"Unknown command #{command}")
        else:
            tree_hash = sys.argv[2]
    # we get the data
    with open(os.path.join(os.getcwd(), ".git/objects", tree_hash[:2], tree_hash[2:]), "rb") as file:
        data = zlib.decompress(file.read())
    _, binary_data = data.split(b'\x00', maxsplit=1)
    while binary_data:
        mode_name, hsh = binary_data.split(b'\x00', maxsplit=1)
        mode, name = mode_name.split()
        if sys.argv[2] == "--name-only":
            print(name.decode("utf-8"))
        else:
            if mode == "blob":
                print(f"100644 {mode.decode("utf-8")} {hsh.decode("utf-8")}\t{name.decode("utf-8")}")
            elif mode == "tree":
                print(f"040000 {mode.decode("utf-8")} {hsh.decode("utf-8")}\t{name.decode("utf-8")}")
            else:
                raise RuntimeError(f"Unknown file type{mode.decode("utf-8")}")
        # here we go to the next item, every SHA hash is 20 bytes long
        binary_data = binary_data[20:]


def main():
    command = sys.argv[1]
    # git init
    if command == "init":
        init()
    # git cat-file -> read blob object
    elif command == "cat-file":
        cat_file(command)
    elif command == "hash-object":
        hash_object(command)
    elif command == "ls-tree":
        ls_tree(command)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
