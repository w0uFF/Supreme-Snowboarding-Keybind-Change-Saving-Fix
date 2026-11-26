#!/usr/bin/env python3
"""Build the exact-version SupremeLight keyboard persistence patch."""
import hashlib, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
EXPECTED = '615fd47962cd174b51f1e466acc7b84d64ce87526c52271c9e12200c730a5c8c'

def align(n): return (n + 0xfff) & ~0xfff

def patch(original):
    if hashlib.sha256(original).hexdigest() != EXPECTED:
        raise ValueError('Unsupported Supreme.exe: original SHA-256 does not match SupremeLight_9617efe6.zip')
    b = bytearray(original)
    u16=lambda x:struct.unpack_from('<H',b,x)[0]
    u32=lambda x:struct.unpack_from('<I',b,x)[0]
    p16=lambda x,v:struct.pack_into('<H',b,x,v)
    p32=lambda x,v:struct.pack_into('<I',b,x,v)
    pe=u32(0x3c); opt=pe+24; sec=opt+u16(pe+20)
    assert u16(pe+6)==4 and u32(opt+28)==0x400000 and u32(opt+56)==0x8a000
    code=(ROOT/'code.bin').read_bytes(); data=bytearray((ROOT/'data.bin').read_bytes()); data.extend(bytes(4096-len(data)))
    drva=0x8b000
    # Preserve all original descriptors (and their existing IATs); append a second
    # KERNEL32 descriptor for the six new APIs. The new IAT lives in writable data.
    old=u32(opt+104); size=u32(opt+108)
    assert old==0x79e58 and size==0x1a4
    desc=original[old:old+size-20]; assert original[old+size-20:old+size]==bytes(20)
    off=0x100; data[off:off+len(desc)]=desc
    names=['CreateFileA','ReadFile','WriteFile','CloseHandle','MoveFileExA','DeleteFileA']
    dll=0x320; data[dll:dll+13]=b'KERNEL32.dll\0'
    lookup=0x300; cursor=0x340; iat=0x6c
    for i,name in enumerate(names):
        entry=b'\0\0'+name.encode('ascii')+b'\0'
        data[cursor:cursor+len(entry)]=entry
        struct.pack_into('<I',data,lookup+4*i,drva+cursor)
        struct.pack_into('<I',data,iat+4*i,drva+cursor)
        cursor=(cursor+len(entry)+1)&~1
    struct.pack_into('<5I',data,off+len(desc),drva+lookup,0,0,drva+dll,drva+iat)
    p32(opt+104,drva+off); p32(opt+108,len(desc)+40)
    # New RX code and RW data sections; preserve debug overlay bytes unchanged.
    raw=align(len(b)); b.extend(bytes(raw-len(b)))
    for i,(name,rva,content,flags) in enumerate([(b'.kbfix',0x8a000,code,0x60000020),(b'.kbdata',drva,data,0xc0000040)]):
        loc=sec+40*(4+i); assert b[loc:loc+40]==bytes(40)
        sz=align(len(content)); struct.pack_into('<8sIIIIIIHHI',b,loc,name,len(content),rva,sz,raw,0,0,0,0,flags)
        b.extend(content); b.extend(bytes(sz-len(content))); raw+=sz
    p16(pe+6,6); p32(opt+4,u32(opt+4)+4096); p32(opt+8,u32(opt+8)+4096); p32(opt+56,0x8c000)
    for va,oldbytes,target in [(0x448598,'6a01898538020000',0x48a000),(0x453887,'ff15b8d44600',0x48a02c),(0x44cd8b,'8b8638020000',0x48a04c)]:
        pos=va-0x400000; oldbytes=bytes.fromhex(oldbytes); assert b[pos:pos+len(oldbytes)]==oldbytes
        b[pos:pos+len(oldbytes)]=b'\xe9'+struct.pack('<i',target-va-5)+b'\x90'*(len(oldbytes)-5)
    return bytes(b)

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('Usage: python patch.py original.exe patched.exe')
    src,dst=map(Path,sys.argv[1:])
    if src.resolve()==dst.resolve(): raise SystemExit('Use a different output path; the original is never overwritten.')
    dst.write_bytes(patch(src.read_bytes()))
    print('Patched SHA-256:',hashlib.sha256(dst.read_bytes()).hexdigest())
