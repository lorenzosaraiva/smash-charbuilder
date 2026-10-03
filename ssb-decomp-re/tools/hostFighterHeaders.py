"""Keep real fighter layouts while removing unused IDO-only declarations."""
import re

def prepare(root, destination):
    # IDO permits extern arrays of not-yet-defined structs. GCC/Clang don't.
    # Only those declarations are omitted; enums and struct layouts stay intact.
    for path in (root/'src/ft/ftchar').glob('*/*.h'):
        text=re.sub(r'^extern (?:FTStatusDesc|FTMotionDesc) .*?;\s*$', '', path.read_text(), flags=re.M)
        target=destination/path.relative_to(root/'src')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    return destination
