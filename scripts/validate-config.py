"""Validate source configuration, optionally requiring a selected build target."""
import argparse
import pathlib
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('path', nargs='?', default='.config')
parser.add_argument('--require-target', action='store_true')
args = parser.parse_args()
settings = {}
for number, line in enumerate(pathlib.Path(args.path).read_text().splitlines(), 1):
    if not line.strip() or line.startswith('#'):
        continue
    match = re.fullmatch(r'(CONFIG_[A-Za-z0-9_]+)=(y|m|n|-?[0-9]+|0x[0-9A-Fa-f]+|"(?:[^"\\]|\\.)*")', line)
    if not match or match[1] in settings:
        parser.error(f'{args.path}:{number}: invalid or duplicate setting: {line!r}')
    settings[match[1]] = match[2]
targets = [key for key, value in settings.items() if key.startswith('CONFIG_TARGET_') and value == 'y']
print(f'{args.path}: {len(settings)} settings, {len(targets)} enabled target entries')
if args.require_target and not targets:
    parser.error('firmware build requires CONFIG_TARGET_*=y; the template has no selected target')
if not settings:
    print('Source template only; firmware build readiness is not verified.')
