import sys, base64
target, b64_str = sys.argv[1], sys.argv[2]
open(target, 'a', encoding='utf-8').write(base64.b64decode(b64_str).decode('utf-8'))
print('Appended to', target)
