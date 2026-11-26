#!/usr/bin/env python3
import struct, sys, hashlib
from pathlib import Path
from patch import patch

def pe(b):
    get=lambda fmt,pos:struct.unpack_from(fmt,b,pos)
    p=get('<I',60)[0]; opt=p+24; n=get('<H',p+6)[0]; start=opt+get('<H',p+20)[0]
    sections=[get('<8sIIIIIIHHI',start+40*i) for i in range(n)]
    def off(rva):
        return next(x[4]+rva-x[2] for x in sections if x[2]<=rva<x[2]+x[3])
    def string(rva):
        return b[off(rva):].split(b'\0',1)[0]
    imports=[]; rva=get('<I',opt+104)[0]; k=0
    while True:
        lut,stamp,chain,name,iat=get('<5I',off(rva)+20*k)
        if not name:break
        syms=[]; j=0
        while True:
            t=get('<I',off(lut)+j*4)[0]
            if not t:break
            syms.append(t&0xffff if t&0x80000000 else string(t+2)); j+=1
        imports.append((string(name),iat,tuple(syms)));k+=1
    return opt,sections,imports

a,b=map(lambda p:Path(p).read_bytes(),sys.argv[1:3]); ao,asec,ai=pe(a); bo,bsec,bi=pe(b)
assert asec==bsec[:4]
assert ai==bi[:len(ai)] and len(ai)==20
assert bi[-1]==(b'KERNEL32.dll',0x8b06c,(b'CreateFileA',b'ReadFile',b'WriteFile',b'CloseHandle',b'MoveFileExA',b'DeleteFileA'))
assert bsec[-2][0].rstrip(b'\0')==b'.kbfix' and bsec[-2][-1]==0x60000020
assert bsec[-1][0].rstrip(b'\0')==b'.kbdata' and bsec[-1][-1]==0xc0000040
assert struct.unpack_from('<I',a,ao+16)==struct.unpack_from('<I',b,bo+16)
assert struct.unpack_from('<I',b,bo+56)[0]==0x8c000
hooks=[(0x448598,8,0x48a000),(0x453887,6,0x48a02c),(0x44cd8b,6,0x48a04c)]
allowed=set()
for va,n,target in hooks:
    x=va-0x400000; assert b[x]==0xe9 and va+5+struct.unpack_from('<i',b,x+1)[0]==target
    assert b[x+5:x+n]==b'\x90'*(n-5);allowed.update(range(x,x+n))
assert all(a[i]==b[i] or i in allowed for i in range(0x1000,len(a)))
assert patch(a)==b
try: patch(b)
except ValueError: pass
else: raise AssertionError('Patched input was not rejected')
print('PASS: Original four section headers and all 20 import descriptors preserved.')
print('PASS: Six additional Win32 imports resolve structurally; original entry point preserved.')
print('PASS: Original section/overlay bytes unchanged except three reviewed instruction sites.')
print('PASS: Three hook jump destinations and padding verified; RX/RW sections separated.')
print('PASS: Deterministic reconstruction and unsupported-version rejection.')
print('Patched SHA-256:',hashlib.sha256(b).hexdigest())
