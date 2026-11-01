from pprint import pprint

from devtools.architecture_manager.scanner import ProjectScanner


def main():

    scanner = ProjectScanner()

    data = scanner.scan()

    print()
    print("=" * 60)
    print(" AI Workspace Architecture Scanner")
    print("=" * 60)

    print()

    print("Project Root :", data["root"])
    print("Directories  :", data["total_directories"])
    print("Python Files :", data["total_python_files"])
    print("Packages     :", len(data["packages"]))

    print()
    print("Packages")
    print("-" * 60)

    for package in data["packages"]:
        print(package)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()