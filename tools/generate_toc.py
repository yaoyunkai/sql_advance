"""
生成标题

Created at 2023/2/21
"""
import os.path
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADV_DIR = os.path.join(BASE_DIR, 'docs', 'advance')
IGNORE_DIR = '.assets'

TITLE_PATTERN = re.compile(r'^(#+) (.*?)$')

GLOBAL_DICT = {
    """
    filename: xxxxx
    
    """
}


def get_titles(dir_path):
    for cur_path in os.listdir(dir_path):
        if cur_path == IGNORE_DIR:
            continue

        full_path = os.path.join(dir_path, cur_path)

        if os.path.isfile(full_path):
            if full_path.endswith(('.md', '.MD')):
                compute_titles(full_path)

        if os.path.isdir(full_path):
            get_titles(full_path)


def compute_titles(file_path):
    try:
        fp = open(file_path, mode='r', encoding='utf8')
        content_lines = fp.readlines()
        fp.close()
    except Exception as e:
        print(e)
        print('can\'t read path: {}'.format(file_path))
        return

    for line in content_lines:
        _match_result = TITLE_PATTERN.match(line)
        if not _match_result:
            continue
        title_level, title_content = _match_result.groups()
        title_level = title_level.count('#')
        print(title_level, title_content)


if __name__ == '__main__':
    # get_titles(ADV_DIR)
    pass
