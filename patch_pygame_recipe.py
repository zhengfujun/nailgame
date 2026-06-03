import re
import sys
import os

path = sys.argv[1]
content = open(path).read()

print("--- Recipe content ---")
print(content)

if 'PYGAME_DETECT_AVX2' in content:
    print("PYGAME_DETECT_AVX2 already present, no patch needed")
    sys.exit(0)

patched = re.sub(
    r"(env\s*=\s*\{[^}]*'PYGAME_CROSS_COMPILE'\s*:\s*'TRUE'[^}]*\})",
    lambda m: m.group(0).replace("'PYGAME_CROSS_COMPILE': 'TRUE'",
                                  "'PYGAME_CROSS_COMPILE': 'TRUE', 'PYGAME_DETECT_AVX2': '0'"),
    content,
    flags=re.DOTALL,
)

patched = re.sub(
    r"(env\[(['\"])PYGAME_CROSS_COMPILE\2\]\s*=\s*(['\"])TRUE\3)",
    r"\1\n        env['PYGAME_DETECT_AVX2'] = '0'",
    patched,
)

if patched == content:
    print("WARNING: regex did not match, appending env export as fallback")
    patched = patched.replace(
        "def build_arch(self",
        "def build_arch(self",
    )
    patched += "\n# patched by CI\nimport os as _os\n_os.environ.setdefault('PYGAME_DETECT_AVX2', '0')\n"

open(path, 'w').write(patched)
print("Patch applied: PYGAME_DETECT_AVX2=0 injected")
print("--- Patched content ---")
print(open(path).read())