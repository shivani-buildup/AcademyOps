import sys
from pathlib import Path

def main():
    main_py_path = Path("src/main.py")
    if not main_py_path.exists():
        print("src/main.py not found.")
        sys.exit(1)

    lines = main_py_path.read_text(encoding="utf-8").splitlines()
    
    # We want to keep lines 1 to 20 (index 0 to 19)
    # We want to replace line 16 (index 15) with standard FastAPI initialization
    # We want to discard lines 21 to 959 (index 20 to 958)
    # We want to keep lines 960 to end (index 959 onwards)
    
    header = lines[0:20]
    # Replace index 15
    for i, line in enumerate(header):
        if "app = FastAPI" in line:
            header[i] = 'app = FastAPI(title="AcademyOps API", version="1.0.0", redoc_url=None)'
            
    footer = lines[959:]
    
    root_route = [
        "",
        "@app.get(\"/\")",
        "def read_root():",
        "    return {\"message\": \"AcademyOps API is running\"}",
        ""
    ]
    
    new_content = "\n".join(header) + "\n" + "\n".join(root_route) + "\n" + "\n".join(footer) + "\n"
    main_py_path.write_text(new_content, encoding="utf-8")
    print("Successfully cleaned src/main.py")

if __name__ == "__main__":
    main()
