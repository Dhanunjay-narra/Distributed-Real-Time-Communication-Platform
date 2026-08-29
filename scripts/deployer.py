import sys, os, base64

def deploy(path, b64_content):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    raw = base64.b64decode(b64_content).decode('utf-8')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(raw.strip() + '\n')
    print(f'[DEPLOYED] {path}')

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        deploy(sys.argv[1], sys.argv[2])
