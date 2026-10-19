#!/usr/bin/env python3
"""Install ZCode's seven code roles and merge their host workflow; dry-run by default."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import tempfile

PACKAGE = Path(__file__).resolve().parents[1]
START = b'<!-- codex-zcode-orchestration:quality:start -->'
END = b'<!-- codex-zcode-orchestration:quality:end -->'
ROLES = ('code-reviewer', 'test-verifier', 'design-critic', 'test-author',
         'finding-validator', 'debugger', 'docs-researcher')



def merge_guidance(original, template):
    block = START + b'\n' + template.strip() + b'\n' + END
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1:
            raise ValueError('Incomplete or duplicate workflow markers in AGENTS.md')
        start, end = original.index(START), original.index(END)
        if end < start:
            raise ValueError('Reversed workflow markers in AGENTS.md')
        return original[:start] + block + original[end + len(END):]
    if original.strip() == template.strip():
        return block + b'\n'
    return original + (b'\n\n' if original else b'') + block + b'\n'


def atomic_write(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.role-install-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def configure(home, model, *, apply=False, replace_existing=False):
    if not re.fullmatch(r'[A-Za-z0-9_.:-]+/[A-Za-z0-9_.:-]+', model):
        raise ValueError('Use the ZCode provider-id/model-id shown in your model settings')
    home = Path(home).expanduser().resolve()
    agents = home / 'agents'
    if agents.is_symlink():
        raise ValueError('Refusing a symlinked agents directory')
    plans = []
    for role in ROLES:
        template = (PACKAGE / 'agents' / (role + '.md')).read_text(encoding='utf-8')
        placeholder = 'model: "__ZCODE_MODEL_ID__"'
        if template.count(placeholder) != 1:
            raise ValueError('Missing model placeholder: ' + role)
        plans.append((agents / (role + '.md'), template.replace(placeholder, 'model: ' + json.dumps(model)).encode('utf-8')))
    guidance = home / 'AGENTS.md'
    if guidance.is_symlink():
        raise ValueError('Refusing a symlinked AGENTS.md')
    original_guidance = guidance.read_bytes() if guidance.exists() else b''
    plans.append((guidance, merge_guidance(original_guidance, (PACKAGE / 'AGENTS.md').read_bytes())))
    changes = []
    conflicts = []
    for path, data in plans:
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError('Refusing non-regular target: ' + str(path))
        original = path.read_bytes() if path.exists() else None
        if original == data:
            continue
        if path != guidance and original is not None and not replace_existing:
            conflicts.append(str(path))
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
        changes.append((path, original, data, mode))
    report = {'apply': apply, 'changed_files': [str(p) for p, _, _, _ in changes],
              'conflicting_roles': conflicts, 'model': model, 'thoughtLevel': 'high',
              'builtins': 'Set Explore and general-purpose to this model / high in ZCode settings'}
    if not apply or not changes:
        return report
    if conflicts:
        raise ValueError('Existing role content differs; inspect dry-run and use --replace-existing only to replace it')
    applied = []
    try:
        for path, original, data, mode in changes:
            current = path.read_bytes() if path.exists() else None
            if path.is_symlink() or current != original:
                raise RuntimeError('Concurrent change: ' + str(path))
            atomic_write(path, data, mode)
            applied.append((path, original, data, mode))
    except BaseException:
        for path, original, data, mode in reversed(applied):
            if path.is_symlink() or path.read_bytes() != data:
                raise RuntimeError('Concurrent change prevents restoration: ' + str(path))
            if original is None:
                path.unlink()
            else:
                atomic_write(path, original, mode)
        raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zcode-home', type=Path, default=Path.home() / '.zcode')
    parser.add_argument('--model', required=True, help='Your provider-id/model-id for Gemini 3.8 Flash')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--replace-existing', action='store_true')
    args = parser.parse_args()
    try:
        report = configure(args.zcode_home, args.model, apply=args.apply, replace_existing=args.replace_existing)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
