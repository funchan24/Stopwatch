#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import argparse
import errno
import os
import platform
import shutil
import stat
from pathlib import Path
from subprocess import PIPE, run
from zipfile import ZipFile

root_dir = Path(__file__).resolve().parents[1]


def get_venv_path():
    venv_dir = root_dir / '.venv'

    os_platform = platform.system()
    if os_platform == 'Windows':
        python_str = 'python'
        python_path = venv_dir / 'scripts' / 'python.exe'
        pip_path = venv_dir / 'scripts' / 'pip.exe'

    elif os_platform == 'Linux':
        python_str = 'python3'
        python_path = venv_dir / 'bin' / 'python3'
        pip_path = venv_dir / 'bin' / 'pip3'

    else:
        raise EnvironmentError('unsupported platform!')

    return python_str, python_path, pip_path


def set_pip(pip_path, python_path):
    cmd_list = [
        f'{pip_path} config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/',
        f'{pip_path} config set global.trusted-host pypi.tuna.tsinghua.edu.cn',
        f'{pip_path} config set global.timeout 6000',
        f'{python_path} -m pip install -U pip'
    ]

    [run(i, shell=True, stdout=PIPE, stderr=PIPE) for i in cmd_list]


def is_empty(folder):
    for f in folder.iterdir():
        return False
    return True


def pack_zip(root_dir, output_dir):
    """package root_dir as zip file, save to output_dir"""

    include_dirs = (root_dir / 'bin', root_dir / 'conf', root_dir / 'core',
                    root_dir / 'docs', root_dir / 'init', root_dir / 'res')
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / (root_dir.name + '.zip')
    if zip_path.exists():
        zip_path.unlink()

    with ZipFile(zip_path, 'w') as z_file:
        for file in root_dir.iterdir():
            if file.is_dir() and not is_empty(
                    file
            ) and file in include_dirs and file.name != '__pycache__':
                for sub_file in file.rglob('*'):
                    if file.parent.name != '__pycache__':
                        z_file.write(sub_file, sub_file.relative_to(root_dir))
            if file.is_file() and file.parent.name != '__pycache__':
                z_file.write(file, file.relative_to(root_dir))


def pack_exe(root_dir, output_dir, pack_cmd):
    """use Nuitka package root_dir as exe file, save to output_dir"""

    def _onerror(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove,
                    os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            func(path)
        else:
            raise

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    try:
        shutil.rmtree(output_dir, onerror=_onerror)
    except FileNotFoundError:
        pass
    output_dir.mkdir(parents=True, exist_ok=True)

    include_dirs = (root_dir / 'bin', root_dir / 'conf', root_dir / 'res')
    for _dir in include_dirs:
        if _dir.exists() and not is_empty(_dir):
            shutil.copytree(_dir, output_dir / _dir.name)

    run(pack_cmd, shell=True)

    for _dir in output_dir.iterdir():
        if '.dist' in _dir.name:
            new_name = _dir.name.replace('.dist', '')
            new_path = _dir.with_name(new_name)
            os.rename(_dir, new_path)


def arg_parse():
    parser = argparse.ArgumentParser(prog='pack',
                                     description='packing python files')

    parser.add_argument('--pack-type', choices=('zip', 'exe'), required=True)
    parser.add_argument('--pack-mode',
                        choices=('typical', 'custom'),
                        required=True)
    parser.add_argument('--extra-option',
                        metavar='',
                        default='',
                        help='use nuitak options')

    return parser.parse_args()


def main():
    os.chdir(root_dir)
    _, venv_python_path, venv_pip_path = get_venv_path()
    set_pip(venv_pip_path, venv_python_path)

    run(f'{venv_pip_path} freeze --exclude Nuitka --exclude yapf >requirements.txt',
        shell=True,
        stdout=PIPE,
        stdin=PIPE)

    args = arg_parse()
    pack_type = args.pack_type
    pack_mode = args.pack_mode
    extra_option = args.extra_option

    if pack_type == 'zip':
        output_dir = root_dir / 'output'
        pack_zip(root_dir, output_dir)
    else:
        run(f'{venv_pip_path} install -U Nuitka',
            shell=True,
            stdout=PIPE,
            stderr=PIPE)
        if pack_mode == 'typical':
            standalone = '--standalone'
            output_dir = Path('output', root_dir.name)
            remove_output = '--remove-output'
            windows_disable_console = '--windows-disable-console'
            windows_icon = Path('res', 'main_256.ico')
            plugin_enable = 'tk-inter'
            target_file = Path('core', 'main.py')
        else:
            standalone = ''
            output_dir = ''
            remove_output = ''
            windows_disable_console = ''
            windows_icon = ''
            plugin_enable = ''
            target_file = ''

        pack_cmd = f'{venv_python_path} -m nuitka' \
                   f' {standalone} ' \
                   f' --output-dir={output_dir} ' \
                   f' {remove_output} ' \
                   f' {windows_disable_console} ' \
                   f' --windows-icon-from-ico={windows_icon} ' \
                   f' --plugin-enable={plugin_enable} ' \
                   f' {extra_option} ' \
                   f' {target_file}'

        pack_exe(root_dir, output_dir, pack_cmd)

    os_platform = platform.system()
    if os_platform == 'Windows':
        run(f'explorer {output_dir}', shell=True, stdout=PIPE, stderr=PIPE)


if __name__ == '__main__':
    main()
