#!/usr/bin/env python3

"""A script that copies metadata from the header of a Notebook.app note to its plist."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import sys
import os
import dateutil.parser as parser
import argparse
import re
import subprocess
import time


def _printable(text):
    return "".join([char for char in text if char.isascii()])

def _plist_from_note(filename):
    filename = os.path.abspath(filename)
    return filename + ".plist"

def _defaults(plist_filename, verb, key, value=None):
    command = f'defaults {verb} "{plist_filename}" {key} {value if value is not None else ""}'
    print(command)
    (exitcode, output) = subprocess.getstatusoutput(command)
    return (exitcode, output)

def _defaults_read(plist_filename, key):
    (exitcode, output) = _defaults(plist_filename, "read", key)
    if exitcode == 0:
        print(f"{key}: {output} from {output}")
        return _printable(output)

def _defaults_read_array(plist_filename, key):
    (exitcode, lines) = _defaults(plist_filename, "read", key)
    if exitcode == 0 and lines:
        output = ""
        for line in lines.splitlines():
            match = re.match(r"\s+(\w+),?", line)
            if match:
                tag = match.group(1)
                output += tag + ", "
        print(f"{key}: {output} from {lines}")
        return _printable(output)

def _defaults_write_date(plist_filename, key, value):
    print(f"setting '{plist_filename}' key {key} to date {value.isoformat()}")
    command = f"defaults write '{plist_filename}' {key} -date '{value.isoformat()}'"
    # print(command)
    os.system(command)

def _defaults_write_string(plist_filename, key, value):
    print(f"setting '{plist_filename}' key {key} to string {value}")
    command = f"defaults write '{plist_filename}' {key} -string '{value}'"
    # print(command)
    os.system(command)

def _defaults_write_array(plist_filename, key, value):
    print(f"setting {plist_filename} key {key} to array {value}")
    command = f"defaults write '{plist_filename}' {key} -array {value}"
    # print(command)
    os.system(command)

def _sync_creation_date(plist_filename, line):
    date_time = parser.parse(line) 
    _defaults_write_date(plist_filename, "CreationDate", date_time)

def _sync_author(plist_filename, line):
    _defaults_write_string(plist_filename, "author", line)

def _sync_source(plist_filename, line):
    _defaults_write_string(plist_filename, "URL", line)

def _sync_description(plist_filename, line):
    _defaults_write_string(plist_filename, "Description", line)

def _sync_tags(plist_filename, line):
    _defaults_write_array(plist_filename, "Tags", line.replace(",", ""))

write_handlers = {
    "clipped: ": _sync_creation_date,
    "author: ": _sync_author,
    "source: ": _sync_source,
    "excerpt: ": _sync_description,
    "tags: ": _sync_tags
}

def _write_plist(filename):
    plist_filename = _plist_from_note(filename)
    print(f"Syncing {filename} -> {plist_filename}")
    with open(filename, 'r', errors='replace') as file:
        parsing = False
        for line in file.readlines():
            if line.startswith('--->'):
                return
            if line.startswith('<!---'):
                print("Starting parsing...")
                parsing = True
            if parsing:
                printable_line = _printable(line).strip()
                for key, handler in write_handlers.items():
                    if printable_line.startswith(key):
                        data = printable_line[len(key):]
                        if data is not None and data != "":
                            handler(plist_filename, data)


def _read_creation_date(plist_filename):
    return _defaults_read(plist_filename, "CreationDate")

def _read_author(plist_filename):
    return _defaults_read(plist_filename, "author")

def _read_source(plist_filename):
    return _defaults_read(plist_filename, "URL")

def _read_description(plist_filename):
    return _defaults_read(plist_filename, "Description")

def _read_tags(plist_filename):
    return _defaults_read_array(plist_filename, "Tags")

read_handlers = {
    "clipped: ": _read_creation_date,
    "author: ": _read_author,
    "source: ": _read_source,
    "excerpt: ": _read_description,
    "tags: ": _read_tags}

def _read_plist(filename):
    plist_filename = _plist_from_note(filename)
    print(f"Syncing {plist_filename} -> {filename}")
    front_matter = "<!---\n"
    for key, handler in read_handlers.items():
        line = handler(plist_filename)
        if line:
            front_matter += f"{key}{line.strip()}\n"
    front_matter += "--->\n\n"
    with open(filename, 'r', errors='replace') as input_file:
        note_data = front_matter + _printable(input_file.read())
        with open(filename, 'w') as output_file:
            output_file.write(note_data)


def _import(filepaths):
    for filepath in filepaths:
    # Import into NoteBooks.app as a new note
        print(f"Importing {filepath} into NoteBooks.app")
        subprocess.run(["open", "-a", "NoteBooks.app", filepath])
        time.sleep(2)
        # Copy medtadata into NoteBooks.app
        filename = os.path.basename(filepath)
        imported_filepath = os.path.expanduser('~') + "/Library/Mobile Documents/iCloud~com~aschmid~notebooks/Documents/Inbox/" + filename
        _write_plist(imported_filepath)
        # Delete the source file we imported
        os.remove(filepath)

def main(argv):
    """Copy metadata."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path and name of the note file.", type=str)
    parser.add_argument("-d", "--dir", help="Path and name of a directory containing note files.", type=str)
    parser.add_argument("-n", "--note", help="Write metadata from the note to the plist.", dest='write', action="store_true", default=False)
    parser.add_argument("-p", "--plist", help="Read metadata from the plist and write to the note.", dest='read', action="store_true", default=False)
    parser.add_argument("-i", "--import", help="Open a file with NoteBooks.app and then copy the metadata from the note to the plist.", dest='import_note', action="store_true", default=False)
    args = parser.parse_args()

    if not args.file and not args.dir:
        print("--file or --dir is required")
        sys.exit()

    if args.write:
        _write_plist(args.file)

    if args.read:
        _read_plist(args.file)

    if args.import_note:
        if args.dir:
            _import([path.path for path in os.scandir(args.dir) if path.is_file() and path.name.endswith(".md")])
        else:
            _import([args.file])

if __name__ == "__main__":
    main(sys.argv[1:])