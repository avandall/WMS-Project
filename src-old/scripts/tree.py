import os

# Cấu hình các thư mục muốn ẨN
IGNORE = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".vscode",
    "env",
    "node_modules",
}


def print_tree(dir_path, prefix=""):
    try:
        # Lấy danh sách file/folder
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return

    # Lọc bỏ các thư mục rác
    entries = [e for e in entries if e not in IGNORE]

    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = i == len(entries) - 1

        print(prefix + ("└── " if is_last else "├── ") + entry)

        if os.path.isdir(path):
            print_tree(path, prefix + ("    " if is_last else "│   "))


if __name__ == "__main__":
    print(f"📂 PROJECT: {os.path.basename(os.getcwd())}")
    print_tree(".")
