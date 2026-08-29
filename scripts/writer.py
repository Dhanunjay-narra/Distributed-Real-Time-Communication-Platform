import os, sys, json, base64

def write_files_from_b64(b64_json):
    data = json.loads(base64.b64decode(b64_json).decode('utf-8'))
    for path, content in data.items():
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        print(f'[CREATED] {path}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        write_files_from_b64(sys.argv[1])
