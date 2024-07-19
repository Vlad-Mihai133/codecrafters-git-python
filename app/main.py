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


def hash_object(file_name):
    with open(file_name,"rb") as file:
        file_content = file.read()
    git_path = os.path.join(os.getcwd(), ".git/objects")
    obj_header = f"blob {len(file_content)}\x00"
    obj_content = obj_header.encode("ascii") + file_content
    sha = hashlib.sha1(obj_content).hexdigest()
    os.mkdir(os.path.join(git_path, sha[:2]))
    with open(os.path.join(git_path, sha[:2], sha[2:]), "wb") as file:
        file.write(zlib.compress(obj_content))
    print(sha, end='')


def main():
    command = sys.argv[1]
    # git init
    if command == "init":
        init()
    # git cat-file -> read blob object
    elif command == "cat-file":
        cat_file(command)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
