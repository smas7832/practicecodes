import os
import tkinter as tk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
import shutil

# Dictionary to map music file extensions to their respective Mutagen classes
music_extensions = {
    '.mp3': MP3,
    '.m4a': MP3,  # Note: m4a is not supported by Mutagen, we use MP3 for simplicity
    '.flac': FLAC,
    '.ogg': OggOpus,
    '.opus': OggOpus,
    '.wav': None  # Note: WAV files have no tags, we skip them
}

# Function to extract album name from music file
def extract_album_name(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in music_extensions:
        if music_extensions[file_ext] is None:
            # For WAV files, we skip extraction
            return file_path
        audio = music_extensions[file_ext](file_path)
        if isinstance(audio, MP3):
            id3 = ID3(file_path)
            if id3.getall('TALB'):
                return id3.getall('TALB')[0].text[0]
        elif isinstance(audio, FLAC) or isinstance(audio, OggOpus):
            return audio.tags['album'][0]
    return file_path

# Function to organize music files
def organize_music_files(source_dir, dest_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            for ext in music_extensions:
                if file.lower().endswith(ext):
                    album_name = extract_album_name(file_path)
                    album_dir = os.path.join(dest_dir, album_name)
                    song_dir = album_dir

                    # Create album directory if it doesn't exist
                    if not os.path.exists(album_dir):
                        os.makedirs(album_dir)

                    # Move music file to album directory
                    shutil.move(file_path, os.path.join(song_dir, file))

                    # Move lyrics file to album directory if it exists
                    lrc_file = file.replace('.mp3', '.lrc') if ext == '.mp3' else file.replace(ext, '.lrc')
                    lrc_path = os.path.join(root, lrc_file)
                    if os.path.exists(lrc_path):
                        shutil.move(lrc_path, os.path.join(song_dir, lrc_file))

# Function to prompt for directories
def prompt_for_dirs():
    root = tk.Tk()
    root.withdraw()
    source_dir = filedialog.askdirectory(title="Select Music Files Directory")
    if not source_dir:
        print("No source directory selected. Exiting.")
        return None, None
    dest_dir = filedialog.askdirectory(title="Select Destination Directory")
    if not dest_dir:
        print("No destination directory selected. Exiting.")
        return None, None
    return source_dir, dest_dir

# Run the music organizer function
def main():
    source_dir, dest_dir = prompt_for_dirs()
    if source_dir and dest_dir:
        organize_music_files(source_dir, dest_dir)
        print("Music files organized successfully!")

if __name__ == "__main__":
    main()