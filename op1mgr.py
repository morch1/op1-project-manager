import click
import readline
import os
import shutil
import sys
from pathlib import Path

PROJECTS_DIR = 'F:\\OP-1\\projects'

def key_prompt(question):
    print(question)
    return click.getchar().lower()


def projects_autocomplete(text, state):
    projects = [p.name for p in sorted(Path(PROJECTS_DIR).iterdir(), key=os.path.getmtime)[::-1] if p.is_dir()]
    results = [p for p in projects if p.startswith(text)] + [None]
    return results[state]


def backup_project(op1_path, album=False):
    name_ok = False
    while not name_ok:
        readline.set_completer(projects_autocomplete)
        name = input('save project as: ')
        readline.set_completer()
        if len(name) == 0:
            continue
        project_dir = Path(PROJECTS_DIR) / Path(name)
        if project_dir.is_dir() and key_prompt(f'project {name} exists. overwrite? (y/N)') == 'y':
                name_ok = True
        else:
            name_ok = True
    project_dir.mkdir(parents=True, exist_ok=True)

    print('backing up tape...')
    op1_tape_dir = op1_path / Path('tape')
    project_tape_dir = project_dir / Path('tape')
    project_tape_dir.mkdir(parents=True, exist_ok=True)
    for f in op1_tape_dir.glob('*.aif'):
        shutil.copy(f, project_tape_dir)

    print('backing up drum presets...')
    op1_drum_dir = op1_path / Path('drum') / Path('user')
    project_drum_dir = project_dir / Path('drum') / Path('user')
    project_drum_dir.mkdir(parents=True, exist_ok=True)
    for f in op1_drum_dir.glob('*.aif'):
        shutil.copy(f, project_drum_dir)

    print('backing up synth presets...')
    op1_synth_dir = op1_path / Path('synth') / Path('user')
    project_synth_dir = project_dir / Path('synth') / Path('user')
    project_synth_dir.mkdir(parents=True, exist_ok=True)
    for f in op1_synth_dir.glob('*.aif'):
        shutil.copy(f, project_synth_dir)

    if album:
        print('backing up album...')
        op1_album_dir = op1_path / Path('album')
        project_album_dir = project_dir / Path('album')
        project_album_dir.mkdir(parents=True, exist_ok=True)
        for f in op1_album_dir.glob('*.aif'):
            shutil.copy(f, project_album_dir)

    print('backup complete!')


def restore_project(op1_path):
    name_ok = False

    while not name_ok:
        readline.set_completer(projects_autocomplete)
        name = input('restore from project: ')
        readline.set_completer()
        if len(name) == 0:
            continue
        project_dir = Path(PROJECTS_DIR) / Path(name)
        if not project_dir.is_dir():
            print(f'invalid project name!')
            continue
        if key_prompt(f'device content will be replaced with project {name}. continue? (y/N)') == 'y':
            name_ok = True
 
    op1_tape_dir = op1_path / Path('tape')
    project_tape_dir = project_dir / Path('tape')
    if project_tape_dir.is_dir():
        print('restoring tape...')
        for f in op1_tape_dir.glob('*.aif'):
            os.remove(f)
        for f in project_tape_dir.glob('*.aif'):
            shutil.copy(f, op1_tape_dir)

    op1_drum_dir = op1_path / Path('drum') / Path('user')
    project_drum_dir = project_dir / Path('drum') / Path('user')
    if project_drum_dir.is_dir():
        print('restoring drum presets...')
        for f in op1_drum_dir.glob('*.aif'):
            os.remove(f)
        for f in project_drum_dir.glob('*.aif'):
            shutil.copy(f, op1_drum_dir)

    op1_synth_dir = op1_path / Path('synth') / Path('user')
    project_synth_dir = project_dir / Path('synth') / Path('user')
    if project_synth_dir.is_dir():
        print('restoring synth presets...')
        for f in op1_synth_dir.glob('*.aif'):
            os.remove(f)
        for f in project_synth_dir.glob('*.aif'):
            shutil.copy(f, op1_synth_dir)

    print('restore complete!')


def backup_snapshots(op1_path):
    print('not implemented')


def erase_tape(op1_path):
    if key_prompt('back up project before erasing tape? (Y/n)') != 'n':
        backup_project(op1_path)
    if key_prompt('tape will be erased. continue? (y/N)') != 'y':
        return
    print('erasing...')
    op1_tape_dir = op1_path / Path('tape')
    for f in op1_tape_dir.glob('*.aif'):
        os.remove(f)
    print('tape erased!')


def main():
    readline.parse_and_bind("tab: complete")

    op1_path = None
    for d in (chr(x) + ":" for x in range(65,91) if Path(chr(x) + ":").exists()):
        if all((Path(d) / Path(p)).exists() for p in ['album', 'drum', 'synth', 'tape']) and shutil.disk_usage(d).total == 402399232:
            op1_path = Path(d)
            break

    if op1_path is None:
        print('op-1 not connected!')
        sys.exit(1)

    print(f'found op-1: {op1_path}')

    action = key_prompt('choose action:\n'
        '- [b]ackup project\n'
        '- backup project + [a]lbum\n'
        '- [r]estore project\n'
        '- backup [s]napshots\n'
        '- [e]rase tape')
    if action == 'b':
        backup_project(op1_path)
    elif action == 'a':
        backup_project(op1_path, album=True)
    elif action == 'r':
        restore_project(op1_path)
    elif action == 's':
        backup_snapshots(op1_path)
    elif action == 'e':
        erase_tape(op1_path)
    key_prompt('press any key to exit')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
