"""Install or check the bounded Ultra/manual entrypoint in personal AGENTS.md."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

START = '<!-- codex-native-orchestrator:activation:start -->'
END = '<!-- codex-native-orchestrator:activation:end -->'


def render_block(skill_dir: Path) -> str:
    skill_dir = skill_dir.resolve()
    if not (skill_dir / 'SKILL.md').is_file():
        raise ValueError('Install codex-native-orchestrator before adding its entrypoint')
    template = (skill_dir / 'references/activation.md').read_text(encoding='utf-8')
    if template.count(START) != 1 or template.count(END) != 1 or template.count('{{SKILL_PATH}}') != 1:
        raise ValueError('Activation template markers or path placeholder are invalid')
    if template.index(START) > template.index(END):
        raise ValueError('Activation template markers are out of order')
    return template.replace('{{SKILL_PATH}}', (skill_dir / 'SKILL.md').as_posix()).strip()


def merge_block(original: bytes, block: str) -> bytes:
    text = original.decode('utf-8-sig')
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ValueError('Existing activation markers are incomplete or duplicated; preserve the file for review')
    if START in text:
        start, end = text.index(START), text.index(END) + len(END)
        if start > text.index(END):
            raise ValueError('Existing activation markers are out of order')
        text = text[:start] + block + text[end:]
    else:
        separator = ('\n' if text.endswith('\n') else '\n\n') if text else ''
        text = text + separator + block + '\n'
    prefix = b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b''
    return prefix + text.encode('utf-8')


def configure(codex_home: Path, apply: bool = False) -> dict:
    codex_home = codex_home.expanduser().resolve()
    skill_dir = codex_home / 'skills/codex-native-orchestrator'
    block = render_block(skill_dir)
    target = codex_home / 'AGENTS.md'
    if target.is_symlink():
        raise ValueError('Refusing to replace a symlink AGENTS.md')
    original = target.read_bytes() if target.exists() else b''
    desired = merge_block(original, block)
    changed = original != desired
    result = {'ok': not changed, 'ultra_ready': not changed, 'changed': changed,
              'path': str(target), 'skill_path': str(skill_dir / 'SKILL.md')}
    if apply and changed:
        fd, temporary = tempfile.mkstemp(prefix='.AGENTS.', dir=codex_home)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(desired)
                handle.flush()
                os.fsync(handle.fileno())
            if (target.read_bytes() if target.exists() else b'') != original:
                raise ValueError('AGENTS.md changed concurrently; no update applied')
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        result.update(ok=True, ultra_ready=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')))
    parser.add_argument('--apply', action='store_true', help='Merge only the marked activation block; default checks without writing')
    args = parser.parse_args(argv)
    try:
        result = configure(args.codex_home, apply=args.apply)
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
