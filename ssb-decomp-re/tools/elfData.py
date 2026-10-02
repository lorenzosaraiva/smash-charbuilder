"""Read the 32-bit ELF sections and symbols used by host/ROM verification."""
import struct

def read_elf(path,endian):
    data=path.read_bytes()
    assert data[:4]==b'\x7fELF' and data[4]==1
    shoff=struct.unpack_from(endian+'I',data,32)[0]
    size,count=struct.unpack_from(endian+'HH',data,46)
    sections=[struct.unpack_from(endian+'10I',data,shoff+i*size) for i in range(count)]
    symbols={}
    for section in sections:
        if section[1]!=2:continue
        strings=sections[section[6]]
        for offset in range(section[4],section[4]+section[5],section[9]):
            name,value,length,info,other,index=struct.unpack_from(endian+'IIIBBH',data,offset)
            start=strings[4]+name
            label=data[start:data.index(b'\0',start)].decode()
            symbols[label]=(value,length,index)
    return data,sections,symbols
