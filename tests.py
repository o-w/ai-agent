# Boot.dev AI-agent assignment test cases.
#
from functions.get_files_info import *

test1 = get_files_info("calculator", ".")
print(test1)

test2 = get_files_info("calculator", "pkg")
print(test2)

print("*******************************\n")
print(
    get_files_info("calculator", "/bin")
)  # should produce error, outside permitted working directory
print(
    get_files_info("calculator", "../")
)  # should produce error, outside permitted working directory
