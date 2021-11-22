#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# python 3.7 or newer


"""
Uninstall or disable android apps list via ADB.
"""


__version__ = "0.0.2"

import argparse
import os
import subprocess

from dataclasses import dataclass, field
from typing import Optional, List
from bisect import bisect_right

# Path to the adb command
ADB: str = "adb"


#------------------------------------------------------------------------------#

# Apps to clean
apps_list_file: str = ""


@dataclass(order=True)
class App:
    """ Android package params """
    name: str
    title: list = field(compare=False)
    uninstall: bool = field(compare=False)  # True - uninstall, False - disable

class AppList (list):
    """
    Sorted list of Android packages
    """

    def insert_sorted(self, app : App) -> None:
        idx = bisect_right(self, app)
        if idx != 0 and self[idx-1] == app:
            if len(app.title) > 0 and (app.title [0] not in self[idx-1].title):
                self[idx-1].title.append (app.title[0])
            return
        self.insert(idx,app)

apps_list : Optional[AppList] = None


#- System utilities -----------------------------------------------------------#

def print_cmd(args: List[str]) -> None:
    for arg in args:
        if arg.find(" ") < 0:
            print(arg, end="")
        else:
            print('"' + arg + '"', end="")
        print(" ", end="")
    print("")


def run_cmd(args: list) -> int:
    print_cmd(args)

    try:
        # os.system () has a bug on Win 7 - can't start command like this:
        # '"c:\\Folder with space\\program" -option "value in quotes"'
        res: int = subprocess.call(args)
    except FileNotFoundError:
        print(f"ADB not found. This path may be wrong:\n {args[0]}")
        raise

    return res


#------------------------------------------------------------------------------#

def split_app_line(line: str) -> Optional[App]:
    line = line.strip()
    if not line:
        return None
    if line.startswith('#'):
        return None

    space = line.find(' ')
    if space != -1:
        name = line[:space]
        title = line[space:].strip()
        if title.startswith('- '):
            title = title[2:].strip()

        uninstall_pos = title.find('[UNINST]')
        uninstall = (uninstall_pos != -1)
        if uninstall:
            title = title[:uninstall_pos].strip()
    else:
        name = line
        title = ''
        uninstall = False

    return App(name, [title], uninstall)


def load_apps_list(file: str) -> None:
    if not os.path.exists(file):
        print (f"File not found: {file}")
        return

    global apps_list
    apps_list = AppList ()
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            a: Optional[App] = split_app_line(line)
            if not a:
                continue
            apps_list.insert_sorted(a)


def show_apps() -> None:
    load_apps_list(apps_list_file)
    if not apps_list:
        return

    print("Apps to clean:")
    for a in apps_list:
        print(f"{a.name} - ", end='')
        for i,title in enumerate (a.title):
            if i > 0:
                print(' ' * (len (a.name) + 3), end='')
            print (f"{title}", end=('\n' if i < len(a.title) - 1 else ''))
        if a.uninstall:
            print (" [UNINSTALL]")
        else:
            print (" [DISABLE]")


def clean_apps(confirm: bool = True) -> None:
    show_apps()
    if not apps_list:
        print("Nothing to do")
        return

    if confirm:
        print("continue [yes | no]?")
        ans: str = input()
        if ans != "yes":
            return

    for a in apps_list:
        cmd: list = [ADB]
        cmd.extend(["shell",
                    "pm",
                    "uninstall" if a.uninstall else "disable-user",
                    "--user",
                    "0"])
        cmd.append(a.name)

        run_cmd(cmd)


#------------------------------------------------------------------------------#

def main() -> None:
    global apps_list_file

    p: argparse.ArgumentParser = argparse.ArgumentParser(
        description=
        "Uninstall or disable android apps by list via ADB\n",
        usage=
        "%(prog)s "
        "[--show] "
        "[--clean] "
        "[--yes] "
        "<apps_list_file>",
        formatter_class=argparse.RawTextHelpFormatter)  # Manual line wrapping

    p.add_argument("-s", "--show",
                   action="store_true",
                   default=False,
                   help="Show list of the apps to delete")

    p.add_argument("-c", "--clean",
                   action="store_true",
                   default=False,
                   help="Uninstall and disable selected apps")

    p.add_argument("-y", "--yes",
                   action="store_true",
                   default=False,
                   help="No confirmation")

    p.add_argument ("apps_list_file",
                    nargs=1,
                    help = "Paths to text file with apps list.")

    args: argparse.Namespace = p.parse_args()

    if args.apps_list_file:
        apps_list_file = args.apps_list_file [0]

    if args.show:
        show_apps()
        return

    if args.clean:
        clean_apps(confirm=not args.yes)
        return

    p.print_help()


if __name__ == "__main__":
    main()
