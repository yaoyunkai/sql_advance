"""


Created at 2023/3/22
"""

import os
import re

# dirs
PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR1 = os.path.join(PROJ_DIR, 'docs', 'SQL进阶教程')

# patterns
TITLE = re.compile(r'^#+ (.*?)$')


def get_titles(dir_path):
    for _path in os.listdir(dir_path):
        if _path == '.assets':
            continue
        print(_path)
        get_file_titles(os.path.join(dir_path, _path))


def get_file_titles(file_path):
    fp = open(file_path, mode='r', encoding='utf8')

    for line in fp.readlines():
        if TITLE.match(line):
            print(line.strip())


if __name__ == '__main__':
    get_titles(DIR1)
