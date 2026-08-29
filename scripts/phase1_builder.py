import os, sys, subprocess, base64

def w(i, c):
    d = os.path.dirname(i)
    if d: os.makedirs(d, exist_ok=True)
    with open(i, 'w', encoding='utf-8') as fh: fh.write(c.strip() + '\n')
    print(f'[OK] {i}')
