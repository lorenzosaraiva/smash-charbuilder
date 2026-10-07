"""Stream exact donor special hitbox samples, preserving native menu RAM."""
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
OUT = ROOT / 'build/char_creator/runtime'
ROM_START = 0x5800000


def generate():
    source = (LAB / 'src/ft/ftspecialtiming.generated.inc').read_text()
    bank = bytearray()
    records = []

    def stream(match):
        name, values = match.groups()
        numbers = [float(v.rstrip('Ff')) for v in re.findall(
            r'-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?[Ff]?', values)]
        assert len(numbers) % 13 == 0, name
        bank.extend(bytes((-len(bank)) % 16))
        offset = len(bank)
        for first in range(0, len(numbers), 13):
            row = numbers[first:first + 13]
            bank.extend(struct.pack('>12fI', *row[:12], int(row[12])))
        records.append(dict(name=name, offset=offset, size=len(bank)-offset))
        return f'#define {name} ((const FTCustomCollisionFrame*)0x{ROM_START+offset:08X})'

    source = re.sub(r'static const FTCustomCollisionFrame (sFTCharBuilderSpecialPath\d+Frames)\[\] = \{(.*?)\n\};',
                    stream, source, flags=re.S)
    assert len(records) == 96, len(records)
    bank.extend(bytes(80 + (-len(bank)) % 16))
    target = OUT / 'include/ft/ftspecialtiming.generated.inc'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)
    (OUT / 'special-collision.bin').write_bytes(bank)
    (OUT / 'special-collision.json').write_text(json.dumps(
        dict(rom_start=ROM_START, size=len(bank), records=records), indent=2)+'\n')


if __name__ == '__main__':
    generate()
