# Boot.dev AI-agent assignment test cases.
#
from functions.get_files_info import *


result = run_python_file(("calculator"), "main.py")
print(result)
result = run_python_file(("calculator"), "main.py", ["3 + 5"])
print(result)
result = run_python_file(("calculator"), "tests.py")
print(result)
result = run_python_file(("calculator"), "../main.py")
print(result)
result = run_python_file(("calculator"), "nonexistent.py")
print(result)
