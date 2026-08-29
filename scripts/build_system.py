import os
import subprocess

def write_file(filepath: str, content: str):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f'[OK] {filepath}')

def write_batch(files_dict: dict):
    for path, content in files_dict.items():
        write_file(path, content)
    print(f'==> Wrote {len(files_dict)} files.')

def git_commit(message: str):
    subprocess.run(['git', 'add', '.'], check=True)
    res = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True)
    print(res.stdout or res.stderr)
