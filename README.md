# MacOS Automation

![Screen shot of Music Cleanup script](https://github.com/tcgoetz/MacOSAutomation/raw/master/ScreenShots/ScreenShot_Music_Cleanup.jpg)

## ![NoteBooks.app](https://www.notebooksapp.com/)

```
usage: sync-note.py [-h] [-f FILE] [-d DIR] [-n] [-p] [-i]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path and name of the note file.
  -d DIR, --dir DIR     Path and name of a directory containing note files.
  -n, --note            Write metadata from the note to the plist.
  -p, --plist           Read metadata from the plist and write to the note.
  -i, --import          Open a file with NoteBooks.app and then copy the metadata from the note to the plist.
```

## EverNote

Scripts for automating Evernote.

Service extensions that:
* Export the current note to the clipboard as simplified and cleaned up HTML.
* Export the selection from the current note to the clipboard as simplified and cleaned up HTML.

Issues these scripts adress:
* When you cut-n-paste from Evernote into an app that takes HTML, the HTML that is pasted does not render the same as in Evernote.
* There is a lot of cruft in Evernote exported HTML.

## Music

I maintain my music library in [Swinsian](https://swinsian.com/), but need to keep Music.app in synch so that my iPhone and iPad get the right data when synching. I've started expermimenting with synching some data like ratings, skips, and playvounts back to Swinsian so that I can make better playlists.

Manage metadata in Music.app:
* Cleanup the Music.app metadata:
  * Clear a tracks skips count when the track hasn't been skipped in skips count weeks.
* Sync recently changed metadata from Swinsian to Music.app.
* Sync recently changed metadata from Music.app to Swinsian.

## Installing

[Download the release file](https://github.com/tcgoetz/EvernoteAutomation/releases) and install according the the instruction in the release readme.

or

Clone the repo and run `make install` in the macos directory.
