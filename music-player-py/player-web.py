# music_player.py
import webui
import pygame
import os
import glob
import time
import threading
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, USLT, APIC
from mutagen import File as MutagenFile # Generic file type
import base64
import io
import tkinter as tk
from tkinter import filedialog

# --- Global State ---
playlist = []
current_song_index = -1
is_playing = False
is_paused = False
current_volume = 0.8  # 0.0 to 1.0
stop_progress_thread = threading.Event()
progress_thread = None
main_window = None # To call JS functions

# --- Pygame Initialization ---
def init_pygame():
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(current_volume)
        print("Pygame initialized successfully.")
    except Exception as e:
        print(f"Error initializing Pygame: {e}")
        # Potentially exit or disable music features
        # For now, we'll let it continue and hope for the best or handle errors in playback functions

# --- Metadata and File Handling ---
def get_audio_metadata(filepath):
    try:
        audio = MutagenFile(filepath, easy=True)
        if audio is None: # Fallback for types easy=True doesn't handle well, e.g. some WAVs
            audio = MutagenFile(filepath) 
        
        meta = {
            'path': filepath,
            'title': audio.get('title', [os.path.basename(filepath)])[0] if audio else os.path.basename(filepath),
            'artist': audio.get('artist', ['Unknown Artist'])[0] if audio else 'Unknown Artist',
            'album': audio.get('album', ['Unknown Album'])[0] if audio else 'Unknown Album',
            'year': str(audio.get('date', [''])[0]).split('-')[0] if audio and 'date' in audio else '', # Take year part
            'duration': 0,
            'album_art_data': None,
            'thumbnail': None, # Will be same as album_art_data for simplicity here
            'lyrics': None
        }

        # Duration
        try:
            # Try pygame first for duration as it's used for playback
            sound = pygame.mixer.Sound(filepath)
            meta['duration'] = sound.get_length()
        except pygame.error:
             if audio and audio.info:
                meta['duration'] = audio.info.length
        
        # Album Art and Lyrics (using non-easy mode for more control)
        try:
            audio_raw = MutagenFile(filepath) # Not easy=True for detailed tags
            if audio_raw:
                # Embedded Album Art
                if isinstance(audio_raw, MP3) and 'APIC:' in audio_raw:
                    for key in audio_raw.keys():
                        if key.startswith('APIC:'):
                            album_art = audio_raw[key]
                            meta['album_art_data'] = f"data:{album_art.mime};base64,{base64.b64encode(album_art.data).decode()}"
                            meta['thumbnail'] = meta['album_art_data'] # Use same for thumbnail
                            break
                elif isinstance(audio_raw, FLAC) and audio_raw.pictures:
                    album_art = audio_raw.pictures[0]
                    meta['album_art_data'] = f"data:{album_art.mime};base64,{base64.b64encode(album_art.data).decode()}"
                    meta['thumbnail'] = meta['album_art_data']
                # Add more formats if needed (e.g., OGG)

                # Embedded Lyrics
                if isinstance(audio_raw, MP3) and 'USLT::XXX' in audio_raw : #XXX for any lang
                     meta['lyrics'] = audio_raw['USLT::XXX'].text
                elif isinstance(audio_raw, MP3) and 'USLT::eng' in audio_raw :
                     meta['lyrics'] = audio_raw['USLT::eng'].text
                elif isinstance(audio_raw, MP3) and 'USLT::   ' in audio_raw : # some files have '   ' as lang
                     meta['lyrics'] = audio_raw['USLT::   '].text
                elif isinstance(audio_raw, FLAC) and 'LYRICS' in audio_raw.tags: # Common but not standard for FLAC
                    meta['lyrics'] = audio_raw.tags['LYRICS'][0]
                elif audio_raw.tags and hasattr(audio_raw.tags, 'getall'): # For ID3 in other formats
                    uslt_frames = audio_raw.tags.getall('USLT')
                    if uslt_frames:
                         meta['lyrics'] = uslt_frames[0].text


        except Exception as e:
            print(f"Error getting detailed metadata for {filepath}: {e}")

        # Fallback: Load .lrc file if no embedded lyrics
        if not meta['lyrics']:
            lrc_path = os.path.splitext(filepath)[0] + ".lrc"
            if os.path.exists(lrc_path):
                try:
                    with open(lrc_path, 'r', encoding='utf-8') as f:
                        # Simple LRC parsing: just get the text, not timed
                        lrc_content = []
                        for line in f:
                            # Remove timestamps like [00:12.34]
                            import re
                            cleaned_line = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', '', line)
                            if cleaned_line.strip():
                                lrc_content.append(cleaned_line.strip())
                        meta['lyrics'] = "\n".join(lrc_content) if lrc_content else None
                except Exception as e:
                    print(f"Error reading LRC file {lrc_path}: {e}")
        
        # Fallback album art from folder (cover.jpg, folder.jpg)
        if not meta['album_art_data']:
            song_dir = os.path.dirname(filepath)
            for art_name in ["cover.jpg", "folder.jpg", "cover.png", "folder.png"]:
                art_path = os.path.join(song_dir, art_name)
                if os.path.exists(art_path):
                    try:
                        with open(art_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode()
                            mime_type = "image/jpeg" if art_name.endswith(".jpg") else "image/png"
                            meta['album_art_data'] = f"data:{mime_type};base64,{encoded_string}"
                            meta['thumbnail'] = meta['album_art_data']
                            break
                    except Exception as e:
                        print(f"Error loading folder art {art_path}: {e}")


        return meta
    except Exception as e:
        print(f"Error processing metadata for {filepath}: {e}")
        return {
            'path': filepath, 'title': os.path.basename(filepath), 'artist': 'Unknown', 
            'album': 'Unknown', 'year': '', 'duration': 0, 'album_art_data': None, 
            'thumbnail': None, 'lyrics': None
        }

# --- Playback Controls ---
def play_song_by_index(index):
    global current_song_index, is_playing, is_paused
    if 0 <= index < len(playlist):
        current_song_index = index
        song = playlist[current_song_index]
        try:
            pygame.mixer.music.load(song['path'])
            pygame.mixer.music.play()
            is_playing = True
            is_paused = False
            update_ui_current_song()
            update_ui_playback_state()
        except Exception as e:
            print(f"Error playing {song['path']}: {e}")
            is_playing = False
            # Optionally inform UI of error

def toggle_play_pause(_event=None): # WebUI passes an event object
    global is_playing, is_paused
    if not playlist or current_song_index == -1:
        if playlist: play_song_by_index(0) # Play first song if none selected
        return

    if is_playing:
        if is_paused:
            pygame.mixer.music.unpause()
            is_paused = False
        else:
            pygame.mixer.music.pause()
            is_paused = True
    else: # Was stopped or playlist just loaded
        play_song_by_index(current_song_index if current_song_index != -1 else 0)
    
    update_ui_playback_state()

def stop_music(_event=None):
    global is_playing, is_paused, current_song_index
    pygame.mixer.music.stop()
    is_playing = False
    is_paused = False
    # current_song_index = -1 # Or keep it to allow play to resume this song
    update_ui_playback_state()
    # Optionally clear current song info or just show as stopped
    if main_window and current_song_index != -1:
         main_window.run_js(f"update_progress(0, {playlist[current_song_index]['duration']});")


def next_song(_event=None):
    global current_song_index
    if not playlist: return
    current_song_index = (current_song_index + 1) % len(playlist)
    play_song_by_index(current_song_index)

def prev_song(_event=None):
    global current_song_index
    if not playlist: return
    current_song_index = (current_song_index - 1 + len(playlist)) % len(playlist)
    play_song_by_index(current_song_index)

def set_volume(event_or_value): # WebUI passes an event object { "arg1": value }
    global current_volume
    if isinstance(event_or_value, webui.event.event): # Called from JS
        volume = event_or_value.arg1 
    else: # Called internally
        volume = event_or_value

    current_volume = max(0.0, min(1.0, float(volume)))
    pygame.mixer.music.set_volume(current_volume)
    if main_window:
        main_window.run_js(f"update_volume({current_volume});")

def seek_music(event): # WebUI passes an event object
    position_sec = event.arg1
    if is_playing and 0 <= current_song_index < len(playlist):
        try:
            # Pygame's seek is for OGG, for MP3 it restarts and plays from beginning up to pos
            # For MP3, it's better to use music.play(start=position_sec) after load
            # However, for simplicity, music.set_pos is attempted.
            # Note: pygame.mixer.music.set_pos() is for position IN SECONDS.
            song_path = playlist[current_song_index]['path']
            
            # Simple seek for now, may not be perfect for all formats / pygame versions
            pygame.mixer.music.play(start=float(position_sec)) 
            if is_paused: # if it was paused, unpause it after seek
                pygame.mixer.music.unpause()
            else: # if it was playing, it will continue from new position
                pass
            
            # If using older pygame or specific formats, this might be needed:
            # pygame.mixer.music.rewind()
            # pygame.mixer.music.set_pos(float(position_sec))
            # if not is_paused: pygame.mixer.music.play() # if it was playing, restart from new pos
            
            print(f"Seeking to {position_sec}s")
        except Exception as e:
            print(f"Error seeking: {e}")


# --- UI Update Functions ---
def update_ui_playlist():
    if main_window:
        # Ensure playlist items are serializable (e.g. no complex objects)
        serializable_playlist = []
        for song in playlist:
            s_song = song.copy() # Make a copy
            # Ensure all values are basic types. Base64 strings are fine.
            serializable_playlist.append(s_song)
        main_window.run_js(f"update_playlist({serializable_playlist});")

def update_ui_current_song():
    if main_window and 0 <= current_song_index < len(playlist):
        song_info = playlist[current_song_index]
        main_window.run_js(f"update_current_song_info({song_info});")
    elif main_window: # No song playing or playlist empty
        main_window.run_js("update_current_song_info(null);")


def update_ui_playback_state():
    if main_window:
        main_window.run_js(f"update_playback_state({str(is_playing).lower()}, {str(is_paused).lower()});")

# --- Progress Thread ---
def song_progress_updater():
    global stop_progress_thread
    while not stop_progress_thread.is_set():
        if is_playing and not is_paused and pygame.mixer.music.get_busy():
            pos_ms = pygame.mixer.music.get_pos()  # Position in milliseconds
            if pos_ms == -1: # Song finished or error
                # Handle song end automatically if needed, or rely on an event
                # For now, just stop updating if -1
                time.sleep(0.2)
                continue

            pos_sec = pos_ms / 1000.0
            if 0 <= current_song_index < len(playlist):
                duration_sec = playlist[current_song_index]['duration']
                if duration_sec > 0 and main_window:
                    main_window.run_js(f"update_progress({pos_sec}, {duration_sec});")
                
                # Auto-next song
                if pos_sec >= duration_sec - 0.5 and duration_sec > 0: # -0.5s buffer
                    print("Song ended, playing next.")
                    main_window.run_js("next_btn.click();") # Simulate click on next
                    # This will trigger next_song Python function via JS which calls play_song_by_index
                    # Need a small sleep to let the JS call chain complete and avoid rapid fire
                    time.sleep(1)


        time.sleep(0.2) # Update interval
    print("Progress thread stopped.")

# --- File Loading ---
def _load_files_from_paths(filepaths):
    global playlist
    if not filepaths: return

    new_songs = []
    total_files = len(filepaths)
    for i, fpath in enumerate(filepaths):
        if main_window:
             main_window.run_js(f"show_loading_feedback('Processing audio files...', { (i+1)/total_files });")
        if os.path.isfile(fpath) and fpath.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
            metadata = get_audio_metadata(fpath)
            new_songs.append(metadata)
    
    playlist.extend(new_songs)
    update_ui_playlist()
    if main_window: main_window.run_js("hide_loading_feedback();")

    if not is_playing and playlist: # If nothing was playing, auto-play first new song
        # play_song_by_index(len(playlist) - len(new_songs) if new_songs else 0)
        pass # Let user decide to play


def load_files(_event=None):
    # This function will be called from JS.
    # It should open a file dialog and then process the selected files.
    # Using tkinter for file dialog as webui's native capabilities can be limited/buggy.
    print("load_files called")
    root = tk.Tk()
    root.withdraw() # Hide the main tkinter window
    root.attributes("-topmost", True) # Bring dialog to front
    filepaths = filedialog.askopenfilenames(
        title="Select Audio Files",
        filetypes=(("Audio Files", "*.mp3 *.wav *.ogg *.flac"), ("All files", "*.*"))
    )
    root.destroy()
    if filepaths:
        # Run loading in a separate thread to not block UI thread from tkinter
        threading.Thread(target=_load_files_from_paths, args=(list(filepaths),)).start()
    else:
        if main_window: main_window.run_js("hide_loading_feedback();")


def load_folder(_event=None):
    print("load_folder called")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_path = filedialog.askdirectory(title="Select Music Folder")
    root.destroy()

    if folder_path:
        if main_window: main_window.run_js(f"show_loading_feedback('Scanning folder...', 0);")
        
        filepaths = []
        # Scan recursively for audio files
        for r, d, f in os.walk(folder_path):
            for file_name in f:
                if file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    filepaths.append(os.path.join(r, file_name))
        
        if filepaths:
             threading.Thread(target=_load_files_from_paths, args=(filepaths,)).start()
        else:
            if main_window: main_window.run_js("hide_loading_feedback();")
            print("No audio files found in folder.")
    else:
        if main_window: main_window.run_js("hide_loading_feedback();")


# --- Lyrics ---
def get_lyrics_for_current_song(_event=None):
    if 0 <= current_song_index < len(playlist):
        song = playlist[current_song_index]
        lyrics = song.get('lyrics') # Already extracted during metadata loading
        if main_window:
            # Need to escape lyrics for JS string. Simplest: use JSON dump then slice quotes
            import json
            js_lyrics = json.dumps(lyrics)[1:-1] if lyrics else ""
            main_window.run_js(f"display_lyrics(`{js_lyrics}`);") # Use template literal for multiline
    elif main_window:
        main_window.run_js("display_lyrics(null);")


# --- Initial Data for UI ---
def get_initial_data(_event=None):
    if main_window:
        update_ui_playlist()
        update_ui_current_song() # Send current song if any (e.g. after reload)
        main_window.run_js(f"update_volume({current_volume});")
        update_ui_playback_state()


# --- WebUI Setup ---
def main():
    global main_window, progress_thread

    init_pygame() # Initialize Pygame mixer

    main_window = webui.window()
    main_window.set_title("Python Music Player")
    
    # Bind Python functions to be callable from JavaScript
    main_window.bind("toggle_play_pause", toggle_play_pause)
    main_window.bind("stop_music", stop_music)
    main_window.bind("next_song", next_song)
    main_window.bind("prev_song", prev_song)
    main_window.bind("set_volume", set_volume)
    main_window.bind("seek_music", seek_music)
    main_window.bind("load_files", load_files)
    main_window.bind("load_folder", load_folder)
    main_window.bind("play_song_by_index", lambda e: play_song_by_index(int(e.arg1)))
    main_window.bind("get_lyrics_for_current_song", get_lyrics_for_current_song)
    main_window.bind("get_initial_data", get_initial_data)

    # Start the progress update thread
    stop_progress_thread.clear()
    progress_thread = threading.Thread(target=song_progress_updater, daemon=True)
    progress_thread.start()

    # Show the UI
    # webui uses a relative path from where python is run, or an absolute path.
    # Best to construct an absolute path to ui/index.html
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_file_path = os.path.join(script_dir, "ui", "index.html")
    
    if not os.path.exists(html_file_path):
        print(f"ERROR: HTML file not found at {html_file_path}")
        print("Make sure you have 'ui/index.html' relative to the script.")
        return

    main_window.show(html_file_path) # Or server a folder using: webui.start_server("ui_folder")
    
    # Cleanup on exit (WebUI blocks until window is closed)
    print("WebUI window closed. Shutting down.")
    stop_progress_thread.set()
    if progress_thread:
        progress_thread.join(timeout=2)
    pygame.mixer.music.stop()
    pygame.quit()
    print("Shutdown complete.")

if __name__ == "__main__":
    main()