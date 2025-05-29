import tkinter
from tkinter import filedialog
import customtkinter as ctk
import pygame
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3
import io
from PIL import Image, ImageTk, ImageDraw, ImageFont
import time
import threading
import re # For parsing LRC files

# --- Constants ---
DEFAULT_ALBUM_ART_PATH = "default_album_art.png"
PLAYLIST_ITEM_THUMBNAIL_SIZE = (50, 50)
MAIN_ALBUM_ART_SIZE = (200, 200)

class PlaylistItemFrame(ctk.CTkFrame): # Unchanged from previous version
    def __init__(self, master, app_ref, song_data, index, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_ref
        self.song_data = song_data
        self.index_in_playlist = index
        self.configure(fg_color="transparent", corner_radius=5)
        self.grid_columnconfigure(1, weight=1)
        thumbnail_image = song_data.get('thumbnail_ctk', self.app.default_playlist_thumbnail_image)
        self.thumbnail_label = ctk.CTkLabel(self, text="", image=thumbnail_image, width=PLAYLIST_ITEM_THUMBNAIL_SIZE[0], height=PLAYLIST_ITEM_THUMBNAIL_SIZE[1])
        self.thumbnail_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="ns")
        title = song_data.get('title', 'Unknown Title')
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=13, weight="bold"), anchor="w", wraplength=350)
        self.title_label.grid(row=0, column=1, padx=(5,0), pady=(5,0), sticky="ew")
        artist = song_data.get('artist', 'Unknown Artist'); album = song_data.get('album', ''); year = song_data.get('year', '')
        details = f"{artist}{f' - {album}' if album else ''}{f' ({year})' if year else ''}"
        self.artist_album_label = ctk.CTkLabel(self, text=details, font=ctk.CTkFont(size=11), anchor="w", wraplength=300)
        self.artist_album_label.grid(row=1, column=1, padx=(5,0), pady=(0,5), sticky="ew")
        duration_str = song_data.get('duration_str', '--:--')
        self.duration_label = ctk.CTkLabel(self, text=duration_str, font=ctk.CTkFont(size=11), anchor="e")
        self.duration_label.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nse")
        for widget in [self, self.title_label, self.artist_album_label, self.thumbnail_label]: widget.bind("<Double-1>", self.on_double_click)
        self.bind("<Enter>", self.on_enter); self.bind("<Leave>", self.on_leave)
        for child in self.winfo_children(): child.bind("<Enter>", self.on_enter_child); child.bind("<Leave>", self.on_leave_child)
    def on_double_click(self, event): self.app.play_song_by_display_index(self.index_in_playlist)
    def on_enter(self, event=None):
        if not self.app.is_song_frame_selected(self): self.configure(fg_color=("#dbdbdb", "#4a4d50"))
    def on_leave(self, event=None):
        if not self.app.is_song_frame_selected(self): self.configure(fg_color="transparent")
    def on_enter_child(self, event=None): self.on_enter()
    def on_leave_child(self, event=None): self.on_leave()
    def update_selection_state(self, is_selected):
        if is_selected:
            sel_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]; 
            sel_color = sel_color[1] if isinstance(sel_color,tuple) and self.app._get_appearance_mode()=="dark" else (sel_color[0] if isinstance(sel_color,tuple) else sel_color)
            self.configure(fg_color=sel_color)
        else:
            self.configure(fg_color="transparent")
            x,y=self.winfo_pointerxy(); widget_under_mouse=self.winfo_containing(x,y)
            if widget_under_mouse==self or widget_under_mouse in self.winfo_children(): self.on_enter()

class MusicPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lyric Master Player") 
        self.geometry("1200x750") # Increased width for lyrics
        ctk.set_appearance_mode("Dark"); ctk.set_default_color_theme("blue")
        pygame.mixer.init()

        self.playlist_data = []; self.original_song_paths_ordered = []
        self.metadata_cache = {} 
        self.current_song_playing_filepath = None; self.current_display_playlist_index = -1
        self.paused = False; self.playing = False; self.current_song_duration_sec = 0
        self.is_loading_songs_flag = False
        self.song_loading_dialog = None; self.generic_processing_dialog = None
        self.lyrics_visible = False # For toggling lyrics pane

        self.create_default_album_art_if_needed()
        self.default_album_art_image = self.load_image_ctk(DEFAULT_ALBUM_ART_PATH, MAIN_ALBUM_ART_SIZE)
        self.default_playlist_thumbnail_image = self.create_placeholder_thumbnail(PLAYLIST_ITEM_THUMBNAIL_SIZE, "♪")

        self.song_frames_in_playlist_display = []
        self.setup_ui()
        self.update_thread_sentinel = threading.Event()
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_default_album_art_if_needed(self): # Unchanged
        if not os.path.exists(DEFAULT_ALBUM_ART_PATH):
            try:
                img=Image.new('RGB',MAIN_ALBUM_ART_SIZE,color=(73,109,137));d=ImageDraw.Draw(img)
                font=ImageFont.load_default();
                try:font=ImageFont.truetype("arial",30)
                except IOError: print("Arial font not found for default art, using PIL default.")
                bbox=d.textbbox((0,0),"No Art",font=font);w=bbox[2]-bbox[0];h=bbox[3]-bbox[1]
                d.text(((MAIN_ALBUM_ART_SIZE[0]-w)/2,(MAIN_ALBUM_ART_SIZE[1]-h)/2-bbox[1]),"No Art",font=font,fill=(255,255,255))
                img.save(DEFAULT_ALBUM_ART_PATH)
            except Exception as e:print(f"Error creating default art: {e}")
    def create_placeholder_thumbnail(self,size,text=""): # Unchanged
        try:
            img=Image.new('RGB',size,color=(50,50,60));d=ImageDraw.Draw(img)
            if text:
                font=ImageFont.load_default();
                try:font=ImageFont.truetype("arial",size[1]//2)
                except IOError: print("Arial font not found for placeholder thumbnail, using PIL default.")
                bbox=d.textbbox((0,0),text,font=font);w=bbox[2]-bbox[0];h=bbox[3]-bbox[1]
                d.text(((size[0]-w)/2,(size[1]-h)/2-bbox[1]),text,font=font,fill=(150,150,180))
            return ctk.CTkImage(light_image=img,dark_image=img,size=size)
        except Exception as e:
            print(f"Error creating placeholder thumb: {e}")
            blank=Image.new('RGB',size,color='black');return ctk.CTkImage(light_image=blank,dark_image=blank,size=size)
    def load_image_ctk(self,path_or_pil,size): # Unchanged
        try:
            img=Image.open(path_or_pil) if isinstance(path_or_pil,str) else path_or_pil
            return ctk.CTkImage(light_image=img,dark_image=img,size=size)
        except:return self.create_placeholder_thumbnail(size,"?")

    def setup_ui(self):
        main_frame=ctk.CTkFrame(self);main_frame.pack(pady=10,padx=10,fill="both",expand=True)
        
        # Top Frame (Album Art & Song Info) - Unchanged
        top_frame=ctk.CTkFrame(main_frame);top_frame.pack(pady=10,padx=10,fill="x")
        self.album_art_label=ctk.CTkLabel(top_frame,text="",image=self.default_album_art_image);self.album_art_label.pack(side="left",padx=10,pady=10)
        info_frame=ctk.CTkFrame(top_frame);info_frame.pack(side="left",padx=10,pady=10,expand=True,fill="x")
        self.song_title_label=ctk.CTkLabel(info_frame,text="Song Title: N/A",font=ctk.CTkFont(size=20,weight="bold"),anchor="w");self.song_title_label.pack(pady=(5,0),fill="x")
        self.artist_label=ctk.CTkLabel(info_frame,text="Artist: N/A",font=ctk.CTkFont(size=16),anchor="w");self.artist_label.pack(pady=(0,5),fill="x")
        self.album_year_label=ctk.CTkLabel(info_frame,text="Album - Year: N/A",font=ctk.CTkFont(size=14),anchor="w");self.album_year_label.pack(pady=(0,5),fill="x")

        # Progress Bar & Time Labels - Unchanged
        progress_frame=ctk.CTkFrame(main_frame);progress_frame.pack(pady=5,padx=10,fill="x")
        self.current_time_label=ctk.CTkLabel(progress_frame,text="00:00",font=ctk.CTkFont(size=12));self.current_time_label.pack(side="left",padx=5)
        self.progress_slider=ctk.CTkSlider(progress_frame,from_=0,to=100,command=self.seek_song);self.progress_slider.set(0);self.progress_slider.configure(state="disabled");self.progress_slider.pack(side="left",padx=5,expand=True,fill="x")
        self.total_time_label=ctk.CTkLabel(progress_frame,text="00:00",font=ctk.CTkFont(size=12));self.total_time_label.pack(side="right",padx=5)
        
        # Controls Frame - Unchanged
        controls_frame=ctk.CTkFrame(main_frame);controls_frame.pack(pady=10,padx=10)
        self.prev_button=ctk.CTkButton(controls_frame,text="⏮",command=self.prev_song,width=50,font=ctk.CTkFont(size=20));self.prev_button.pack(side="left",padx=5)
        self.play_pause_button=ctk.CTkButton(controls_frame,text="▶",command=self.toggle_play_pause,width=70,font=ctk.CTkFont(size=20));self.play_pause_button.pack(side="left",padx=5)
        self.stop_button=ctk.CTkButton(controls_frame,text="⏹",command=self.stop_song,width=50,font=ctk.CTkFont(size=20));self.stop_button.pack(side="left",padx=5)
        self.next_button=ctk.CTkButton(controls_frame,text="⏭",command=self.next_song,width=50,font=ctk.CTkFont(size=20));self.next_button.pack(side="left",padx=5)
        volume_frame=ctk.CTkFrame(controls_frame);volume_frame.pack(side="left",padx=20,fill="x",expand=True)
        ctk.CTkLabel(volume_frame,text="🔊",font=ctk.CTkFont(size=18)).pack(side="left")
        self.volume_slider=ctk.CTkSlider(volume_frame,from_=0,to=1,command=self.set_volume);self.volume_slider.set(0.5);pygame.mixer.music.set_volume(0.5);self.volume_slider.pack(side="left",padx=5,expand=True,fill="x")

        # --- Middle Content Area (Playlist & Lyrics) ---
        self.middle_content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.middle_content_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.middle_content_frame.grid_columnconfigure(0, weight=1) # Playlist column
        self.middle_content_frame.grid_columnconfigure(1, weight=0) # Lyrics column (initially no weight)
        self.middle_content_frame.grid_rowconfigure(1, weight=1) # Row for playlist/lyrics content

        # Lyrics Toggle Button (above playlist/lyrics)
        lyrics_toggle_frame = ctk.CTkFrame(self.middle_content_frame, fg_color="transparent")
        lyrics_toggle_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,5))
        self.lyrics_toggle_button = ctk.CTkButton(lyrics_toggle_frame, text="Show Lyrics", command=self.toggle_lyrics_pane, width=120)
        self.lyrics_toggle_button.pack(side="right", padx=5)
        
        # Playlist Container (remains mostly same, but placed in grid)
        self.playlist_container_frame = ctk.CTkFrame(self.middle_content_frame)
        self.playlist_container_frame.grid(row=1, column=0, sticky="nsew", padx=(0,5)) # Note padx for spacing
        playlist_header=ctk.CTkFrame(self.playlist_container_frame,fg_color="transparent");playlist_header.pack(fill="x",pady=(0,5))
        ctk.CTkLabel(playlist_header,text="Playlist",font=ctk.CTkFont(size=16,weight="bold")).pack(side="left",padx=(5,0))
        self.sort_options=["Added Order","Title","Artist","Album","Year","Duration"]
        self.sort_var=tkinter.StringVar(value=self.sort_options[0])
        self.sort_menu=ctk.CTkOptionMenu(playlist_header,values=self.sort_options,variable=self.sort_var,command=self.sort_playlist_with_dialog);self.sort_menu.pack(side="right",padx=5)
        ctk.CTkLabel(playlist_header,text="Sort by:",font=ctk.CTkFont(size=12)).pack(side="right")
        self.playlist_scrollable_frame=ctk.CTkScrollableFrame(self.playlist_container_frame,label_text="",fg_color=("gray85","gray18"));self.playlist_scrollable_frame.pack(fill="both",expand=True)

        # Lyrics Display Area (initially hidden)
        self.lyrics_display_frame = ctk.CTkFrame(self.middle_content_frame)
        # self.lyrics_display_frame.grid(row=1, column=1, sticky="nsew", padx=(5,0)) # Will be gridded by toggle function
        ctk.CTkLabel(self.lyrics_display_frame, text="Lyrics", font=ctk.CTkFont(size=16,weight="bold")).pack(pady=(0,5), padx=5, anchor="w")
        self.lyrics_textbox = ctk.CTkTextbox(self.lyrics_display_frame, wrap="word", state="disabled", font=("Arial", 12)) # Or your preferred font
        self.lyrics_textbox.pack(fill="both", expand=True, padx=5, pady=(0,5))

        # File Buttons Frame - Unchanged
        file_buttons=ctk.CTkFrame(main_frame);file_buttons.pack(pady=10,padx=10,fill="x",side="bottom")
        self.load_file_button=ctk.CTkButton(file_buttons,text="Load File",command=self.load_file);self.load_file_button.pack(side="left",padx=5,expand=True)
        self.load_folder_button=ctk.CTkButton(file_buttons,text="Load Folder",command=self.load_folder);self.load_folder_button.pack(side="left",padx=5,expand=True)

        self.update_lyrics_pane_visibility() # Initial setup

    def toggle_lyrics_pane(self):
        self.lyrics_visible = not self.lyrics_visible
        self.update_lyrics_pane_visibility()

    def update_lyrics_pane_visibility(self):
        if self.lyrics_visible:
            self.lyrics_display_frame.grid(row=1, column=1, sticky="nsew", padx=(5,0))
            self.middle_content_frame.grid_columnconfigure(1, weight=1) # Give lyrics pane weight
            self.lyrics_toggle_button.configure(text="Hide Lyrics")
            self.update_lyrics_display() # Update lyrics if a song is playing
        else:
            self.lyrics_display_frame.grid_remove()
            self.middle_content_frame.grid_columnconfigure(1, weight=0) # Remove lyrics pane weight
            self.lyrics_toggle_button.configure(text="Show Lyrics")
        # Ensure playlist takes full width if lyrics are hidden
        self.middle_content_frame.grid_columnconfigure(0, weight=1)


    def update_lyrics_display(self):
        if not self.lyrics_visible or not hasattr(self, 'lyrics_textbox') or not self.lyrics_textbox.winfo_exists():
            return

        self.lyrics_textbox.configure(state="normal")
        self.lyrics_textbox.delete("1.0", "end")
        
        lyrics_text = "Lyrics not available for this song."
        if self.current_display_playlist_index != -1 and self.playlist_data:
            current_song_data = self.playlist_data[self.current_display_playlist_index]
            if current_song_data.get('lyrics'):
                lyrics_text = current_song_data['lyrics']
        
        self.lyrics_textbox.insert("1.0", lyrics_text)
        self.lyrics_textbox.configure(state="disabled")


    def _parse_lrc_file(self, lrc_filepath):
        lyrics_lines = []
        try:
            with open(lrc_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Simple parsing: remove timestamps like [00:12.34] and metadata tags like [ti:Title]
                    # More advanced parsing could handle synchronization.
                    line_text = re.sub(r'\[[0-9]{2}:[0-9]{2}\.[0-9]{2,3}\]', '', line) # Timestamps
                    line_text = re.sub(r'\[[a-zA-Z]{2,}:.*?\]', '', line_text) # Metadata tags
                    if line_text: # Add if not empty after stripping
                        lyrics_lines.append(line_text)
            return "\n".join(lyrics_lines) if lyrics_lines else None
        except FileNotFoundError:
            # print(f"LRC file not found: {lrc_filepath}")
            return None
        except Exception as e:
            print(f"Error parsing LRC file {lrc_filepath}: {e}")
            return None

    # --- Dialogs (show_song_loading_dialog, etc.) - Unchanged ---
    def _center_popup(self, popup, width, height):
        x=(self.winfo_screenwidth()//2)-(width//2);y=(self.winfo_screenheight()//2)-(height//2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
    def show_song_loading_dialog(self, message="Loading songs..."):
        if self.song_loading_dialog and self.song_loading_dialog.winfo_exists(): self.song_loading_dialog.destroy()
        self.song_loading_dialog=ctk.CTkToplevel(self);self.song_loading_dialog.title("Loading")
        self._center_popup(self.song_loading_dialog,350,130)
        self.song_loading_dialog.transient(self);self.song_loading_dialog.grab_set()
        self.song_loading_dialog.protocol("WM_DELETE_WINDOW",lambda:None);self.song_loading_dialog.resizable(False,False)
        self.loading_label_in_dialog=ctk.CTkLabel(self.song_loading_dialog,text=message,font=ctk.CTkFont(size=14));self.loading_label_in_dialog.pack(pady=(20,10),padx=20)
        self.song_loading_progressbar=ctk.CTkProgressBar(self.song_loading_dialog,mode="indeterminate",height=10);self.song_loading_progressbar.pack(pady=(0,20),padx=30,fill="x")
        self.song_loading_progressbar.start();self.is_loading_songs_flag=True
        if hasattr(self,'load_file_button') and self.load_file_button.winfo_exists(): self.load_file_button.configure(state="disabled")
        if hasattr(self,'load_folder_button') and self.load_folder_button.winfo_exists(): self.load_folder_button.configure(state="disabled")
        if hasattr(self,'sort_menu') and self.sort_menu.winfo_exists(): self.sort_menu.configure(state="disabled")
        if hasattr(self,'lyrics_toggle_button') and self.lyrics_toggle_button.winfo_exists(): self.lyrics_toggle_button.configure(state="disabled")
    def hide_song_loading_dialog(self):
        if self.song_loading_dialog and self.song_loading_dialog.winfo_exists():
            self.song_loading_progressbar.stop();self.song_loading_dialog.grab_release();self.song_loading_dialog.destroy()
        self.song_loading_dialog=None;self.is_loading_songs_flag=False
        if hasattr(self,'load_file_button') and self.load_file_button.winfo_exists(): self.load_file_button.configure(state="normal")
        if hasattr(self,'load_folder_button') and self.load_folder_button.winfo_exists(): self.load_folder_button.configure(state="normal")
        if hasattr(self,'sort_menu') and self.sort_menu.winfo_exists(): self.sort_menu.configure(state="normal")
        if hasattr(self,'lyrics_toggle_button') and self.lyrics_toggle_button.winfo_exists(): self.lyrics_toggle_button.configure(state="normal")
    def show_generic_processing_dialog(self, message="Processing..."):
        if self.generic_processing_dialog and self.generic_processing_dialog.winfo_exists():self.generic_processing_dialog.destroy()
        self.generic_processing_dialog=ctk.CTkToplevel(self);self.generic_processing_dialog.title("Processing")
        self._center_popup(self.generic_processing_dialog,300,100)
        self.generic_processing_dialog.transient(self);self.generic_processing_dialog.grab_set()
        self.generic_processing_dialog.protocol("WM_DELETE_WINDOW",lambda:None);self.generic_processing_dialog.resizable(False,False)
        ctk.CTkLabel(self.generic_processing_dialog,text=message,font=ctk.CTkFont(size=14)).pack(pady=20,padx=20,expand=True)
    def hide_generic_processing_dialog(self):
        if self.generic_processing_dialog and self.generic_processing_dialog.winfo_exists():
            self.generic_processing_dialog.grab_release();self.generic_processing_dialog.destroy()
        self.generic_processing_dialog=None

    def get_song_metadata(self, song_path):
        if song_path in self.metadata_cache:
            # Ensure lyrics are checked if they weren't before or if policy changes
            cached_data = self.metadata_cache[song_path].copy()
            if 'lyrics' not in cached_data: # If lyrics weren't loaded before for this cached item
                lrc_path = os.path.splitext(song_path)[0] + ".lrc"
                cached_data['lyrics'] = self._parse_lrc_file(lrc_path)
                self.metadata_cache[song_path]['lyrics'] = cached_data['lyrics'] # Update cache
            return cached_data

        filename = os.path.basename(song_path)
        song_data = {'filepath':song_path,'title':filename,'artist':"Unknown Artist",'album':"Unknown Album",'year':"",'duration_sec':0,'duration_str':"00:00",'album_art_pil':None,'thumbnail_ctk':self.default_playlist_thumbnail_image, 'lyrics': None}
        
        # --- Metadata and Album Art (Same as before) ---
        try:
            ext = os.path.splitext(song_path)[1].lower(); audio = None
            if ext == ".mp3":
                audio = MP3(song_path,ID3=EasyID3)
                if audio:
                    if 'title' in audio and audio['title']: song_data['title']=audio['title'][0]
                    if 'artist' in audio and audio['artist']: song_data['artist']=audio['artist'][0]
                    if 'album' in audio and audio['album']: song_data['album']=audio['album'][0]
                    if 'date' in audio and audio['date'] and audio['date'][0]: song_data['year']=audio['date'][0][:4]
                    audio_id3 = ID3(song_path) 
                    for tag in audio_id3.values():
                        if isinstance(tag,APIC): song_data['album_art_pil']=Image.open(io.BytesIO(tag.data)); break
            # ... (FLAC, OGG handling - same as before) ...
            elif ext == ".flac":
                audio = FLAC(song_path)
                if audio:
                    if 'title' in audio and audio['title']: song_data['title']=audio['title'][0]
                    if 'artist' in audio and audio['artist']: song_data['artist']=audio['artist'][0]
                    if 'album' in audio and audio['album']: song_data['album']=audio['album'][0]
                    if 'date' in audio and audio['date'] and audio['date'][0]: song_data['year']=audio['date'][0][:4]
                    if audio.pictures: song_data['album_art_pil']=Image.open(io.BytesIO(audio.pictures[0].data))
            elif ext == ".ogg":
                audio = OggVorbis(song_path)
                if audio:
                    if 'title' in audio and audio['title']: song_data['title']=audio['title'][0]
                    if 'artist' in audio and audio['artist']: song_data['artist']=audio['artist'][0]
                    if 'album' in audio and audio['album']: song_data['album']=audio['album'][0]
                    if 'date' in audio and audio['date'] and audio['date'][0]: song_data['year']=audio['date'][0][:4]

            if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'): song_data['duration_sec']=audio.info.length
            else: 
                try: temp_sound=pygame.mixer.Sound(song_path);song_data['duration_sec']=temp_sound.get_length();del temp_sound
                except pygame.error: pass 
            
            if song_data['duration_sec']>0: song_data['duration_str']=self.format_time(song_data['duration_sec'])
            if song_data['album_art_pil']:
                thumb_pil = song_data['album_art_pil'].copy(); thumb_pil.thumbnail(PLAYLIST_ITEM_THUMBNAIL_SIZE,Image.Resampling.LANCZOS)
                song_data['thumbnail_ctk']=self.load_image_ctk(thumb_pil,PLAYLIST_ITEM_THUMBNAIL_SIZE)
        except Exception as e:
            print(f"General metadata error for {filename}: {e}")
            if song_data['duration_sec'] == 0:
                try: temp_sound=pygame.mixer.Sound(song_path);song_data['duration_sec']=temp_sound.get_length();del temp_sound
                except pygame.error: pass
                if song_data['duration_sec'] > 0: song_data['duration_str'] = self.format_time(song_data['duration_sec'])

        # --- Load Lyrics ---
        lrc_filepath = os.path.splitext(song_path)[0] + ".lrc"
        song_data['lyrics'] = self._parse_lrc_file(lrc_filepath)
        
        self.metadata_cache[song_path] = song_data.copy() 
        return song_data.copy()

    # --- Threaded Loading and Finalizing (largely same) ---
    def _threaded_load_and_process_songs(self, filepaths_to_load):
        processed_data_for_this_request = []
        for path in filepaths_to_load:
            song_data = self.get_song_metadata(path) 
            processed_data_for_this_request.append(song_data)
        if hasattr(self, 'after') and self.winfo_exists(): # Check if app still exists
            self.after(0, self._finalize_song_loading, processed_data_for_this_request, filepaths_to_load)

    def _finalize_song_loading(self, processed_data_for_this_request, original_filepaths_from_this_load_request):
        self.hide_song_loading_dialog()
        made_changes_to_playlist_display = False

        for song_data in processed_data_for_this_request:
            if not any(orig_path == song_data['filepath'] for orig_path in self.original_song_paths_ordered):
                self.original_song_paths_ordered.append(song_data['filepath'])
            # Ensure song_data is added/updated in self.playlist_data
            found_in_playlist = False
            for i, existing_sd in enumerate(self.playlist_data):
                if existing_sd['filepath'] == song_data['filepath']:
                    self.playlist_data[i] = song_data # Update if exists
                    found_in_playlist = True
                    made_changes_to_playlist_display = True # Potentially new metadata (e.g. lyrics)
                    break
            if not found_in_playlist:
                self.playlist_data.append(song_data)
                made_changes_to_playlist_display = True
        
        if made_changes_to_playlist_display or not self.song_frames_in_playlist_display:
            self.sort_playlist(self.sort_var.get(), use_dialog=False) 
            if not self.playing and not self.paused and original_filepaths_from_this_load_request:
                first_req_path = original_filepaths_from_this_load_request[0]
                try:
                    idx_to_play = next(i for i,data in enumerate(self.playlist_data) if data['filepath']==first_req_path)
                    self.play_song_by_display_index(idx_to_play)
                except StopIteration:
                    if self.playlist_data: self.play_song_by_display_index(0)
        elif self.playlist_data and self.current_display_playlist_index == -1:
             self.current_display_playlist_index = 0; self.update_current_playlist_item_highlight()

    def load_file(self): # Unchanged
        if self.is_loading_songs_flag: return
        filepath = filedialog.askopenfilename(defaultextension=".mp3",filetypes=[("Audio Files","*.mp3 *.wav *.ogg *.flac"),("All Files","*.*")])
        if filepath:
            self.show_song_loading_dialog("Loading file...")
            threading.Thread(target=self._threaded_load_and_process_songs,args=([filepath],),daemon=True).start()

    def load_folder(self): # Unchanged (except added winfo_exists for dialog label)
        if self.is_loading_songs_flag: return
        folderpath = filedialog.askdirectory()
        if folderpath:
            self.show_song_loading_dialog("Scanning folder...")
            def scan_then_process(folder_path_param):
                songs_in_folder = []
                for root,_,files in os.walk(folder_path_param):
                    for file in files:
                        if file.lower().endswith((".mp3",".wav",".ogg",".flac")): songs_in_folder.append(os.path.join(root,file))
                
                if songs_in_folder:
                    if hasattr(self, 'song_loading_dialog') and self.song_loading_dialog and self.song_loading_dialog.winfo_exists() and hasattr(self, 'loading_label_in_dialog'):
                        if self.winfo_exists(): # Check main app window
                           self.after(0, lambda: self.loading_label_in_dialog.configure(text=f"Processing {len(songs_in_folder)} songs..."))
                    self._threaded_load_and_process_songs(songs_in_folder)
                else:
                    if hasattr(self, 'after') and self.winfo_exists(): self.after(0, self.hide_song_loading_dialog) 
            threading.Thread(target=scan_then_process,args=(folderpath,),daemon=True).start()

    def repopulate_playlist_display(self): # Unchanged
        if not (hasattr(self, 'playlist_scrollable_frame') and self.playlist_scrollable_frame.winfo_exists()): return
        for widget in self.playlist_scrollable_frame.winfo_children(): widget.destroy()
        self.song_frames_in_playlist_display = []
        if not self.playlist_data:
            ctk.CTkLabel(self.playlist_scrollable_frame,text="Playlist is empty.",text_color="gray").pack(pady=20,padx=20,expand=True); return
        for i,song_data in enumerate(self.playlist_data):
            item_frame = PlaylistItemFrame(self.playlist_scrollable_frame,self,song_data,i,height=65)
            item_frame.pack(fill="x",pady=(2,0),padx=2); self.song_frames_in_playlist_display.append(item_frame)
        self.update_current_playlist_item_highlight()

    def update_current_playlist_item_highlight(self): # Unchanged
        if not (hasattr(self, 'song_frames_in_playlist_display')): return
        for i,frame in enumerate(self.song_frames_in_playlist_display):
            if frame.winfo_exists(): frame.update_selection_state(i == self.current_display_playlist_index)
        if self.current_display_playlist_index!=-1 and hasattr(self, 'playlist_scrollable_frame') and self.playlist_scrollable_frame.winfo_exists() and self.song_frames_in_playlist_display:
             if hasattr(self.playlist_scrollable_frame, '_parent_canvas') and self.playlist_scrollable_frame._parent_canvas.winfo_exists():
                self.playlist_scrollable_frame._parent_canvas.after(50, lambda idx=self.current_display_playlist_index: self._scroll_to_index(idx))
    def _scroll_to_index(self, index): # Unchanged
        if not (0<=index<len(self.song_frames_in_playlist_display)) or \
           not (hasattr(self.playlist_scrollable_frame,'_parent_canvas') and self.playlist_scrollable_frame._parent_canvas.winfo_exists()): return
        total_items=len(self.song_frames_in_playlist_display)
        if total_items>0: self.playlist_scrollable_frame._parent_canvas.yview_moveto(index/total_items if total_items > 1 else 0.0)
    def is_song_frame_selected(self,frame_to_check): # Unchanged
        try: return self.song_frames_in_playlist_display.index(frame_to_check)==self.current_display_playlist_index
        except (ValueError, AttributeError): return False

    def sort_playlist_with_dialog(self, sort_key_from_menu): # Unchanged
        self.show_generic_processing_dialog(f"Sorting by {sort_key_from_menu}...")
        self.after(50, lambda sk=sort_key_from_menu: self.sort_playlist(sk, use_dialog=True))
        
    def sort_playlist(self, sort_key, use_dialog=False): # Unchanged (uses corrected helpers)
        if self.is_loading_songs_flag:
            if use_dialog and hasattr(self, 'hide_generic_processing_dialog'): self.hide_generic_processing_dialog()
            return

        current_playing_path = self.current_song_playing_filepath

        def safe_lower(s_val): return (s_val or "").lower()
        def safe_year_key(s_item): year_val = s_item.get('year', '0000'); return year_val if year_val else '0000'

        if sort_key == "Added Order":
            temp_map = {data['filepath']: data for data in self.playlist_data}
            self.playlist_data = [temp_map[p] for p in self.original_song_paths_ordered if p in temp_map]
        elif sort_key == "Title": self.playlist_data.sort(key=lambda s_item: safe_lower(s_item.get('title')))
        elif sort_key == "Artist": self.playlist_data.sort(key=lambda s_item: safe_lower(s_item.get('artist')))
        elif sort_key == "Album": self.playlist_data.sort(key=lambda s_item: safe_lower(s_item.get('album')))
        elif sort_key == "Year": self.playlist_data.sort(key=safe_year_key)
        elif sort_key == "Duration": self.playlist_data.sort(key=lambda s_item: s_item.get('duration_sec', 0))

        if current_playing_path:
            try: self.current_display_playlist_index = next(i for i, data in enumerate(self.playlist_data) if data['filepath'] == current_playing_path)
            except StopIteration: self.current_display_playlist_index = -1
        elif self.playlist_data: self.current_display_playlist_index = 0
        else: self.current_display_playlist_index = -1

        if hasattr(self, 'repopulate_playlist_display'): self.repopulate_playlist_display()
        if use_dialog and hasattr(self, 'hide_generic_processing_dialog'): self.hide_generic_processing_dialog()

    def play_song_by_display_index(self, display_index):
        if not(0<=display_index<len(self.playlist_data)):self.stop_song();return
        self.current_display_playlist_index=display_index;song_data=self.playlist_data[display_index].copy()
        self.current_song_playing_filepath=song_data['filepath']
        try:
            pygame.mixer.music.load(self.current_song_playing_filepath);pygame.mixer.music.play()
            self.playing=True;self.paused=False
            if hasattr(self,'play_pause_button') and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="⏸")
            if hasattr(self,'progress_slider') and self.progress_slider.winfo_exists(): self.progress_slider.configure(state="normal")
            self.update_main_song_info(song_data)
            self.update_current_playlist_item_highlight()
            self.update_lyrics_display() # Update lyrics when song changes
        except pygame.error as e:
            print(f"Error playing {self.current_song_playing_filepath}: {e}") # ... (error handling)

    def update_main_song_info(self, song_data): # Unchanged
        if not hasattr(self, 'song_title_label') or not self.song_title_label.winfo_exists(): return 
        self.song_title_label.configure(text=f"{song_data.get('title','N/A')}")
        self.artist_label.configure(text=f"{song_data.get('artist','N/A')}")
        album_year_str = song_data.get('album','N/A')
        if song_data.get('year'): album_year_str += f" - {song_data.get('year')}"
        self.album_year_label.configure(text=album_year_str)
        art_img=self.load_image_ctk(song_data.get('album_art_pil'),MAIN_ALBUM_ART_SIZE) if song_data.get('album_art_pil') else self.default_album_art_image
        self.album_art_label.configure(image=art_img);self.album_art_label.image=art_img
        self.current_song_duration_sec=song_data.get('duration_sec',0)
        self.total_time_label.configure(text=self.format_time(self.current_song_duration_sec if self.current_song_duration_sec>0 else 0))
        self.progress_slider.configure(to=100 if self.current_song_duration_sec>0 else 1)

    def toggle_play_pause(self): # Unchanged
        if not self.playlist_data:return
        if self.current_display_playlist_index==-1 and self.playlist_data:self.play_song_by_display_index(0);return
        if self.playing:pygame.mixer.music.pause();self.paused=True;self.playing=False;self.play_pause_button.configure(text="▶")
        elif self.paused:pygame.mixer.music.unpause();self.paused=False;self.playing=True;self.play_pause_button.configure(text="⏸")
        else:self.play_song_by_display_index(self.current_display_playlist_index if self.current_display_playlist_index!=-1 else 0)

    def stop_song(self):
        pygame.mixer.music.stop();self.playing=False;self.paused=False;self.current_song_playing_filepath=None
        if hasattr(self,'play_pause_button') and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
        if hasattr(self,'song_title_label') and self.song_title_label.winfo_exists(): self.song_title_label.configure(text="Song Title: N/A")
        # ... (rest of UI updates for stop - same as before) ...
        self.current_song_duration_sec=0; self.update_current_playlist_item_highlight()
        self.update_lyrics_display() # Clear lyrics on stop or show "N/A"

    def next_song(self): # Unchanged
        if not self.playlist_data:return;idx=0 if self.current_display_playlist_index==-1 else (self.current_display_playlist_index+1)%len(self.playlist_data);self.play_song_by_display_index(idx)
    def prev_song(self): # Unchanged
        if not self.playlist_data:return;idx=len(self.playlist_data)-1 if self.current_display_playlist_index==-1 else (self.current_display_playlist_index-1+len(self.playlist_data))%len(self.playlist_data);self.play_song_by_display_index(idx)
    def set_volume(self,value):pygame.mixer.music.set_volume(float(value)) # Unchanged
    def seek_song(self,value): # Unchanged
        if(self.playing or self.paused)and self.current_song_duration_sec>0:
            pos=(float(value)/100.0)*self.current_song_duration_sec;pygame.mixer.music.set_pos(pos)
            if hasattr(self,'current_time_label') and self.current_time_label.winfo_exists(): self.current_time_label.configure(text=self.format_time(pos))
    def format_time(self,s):return time.strftime('%M:%S',time.gmtime(float(s))) # Unchanged

    def update_progress(self): # Unchanged (with winfo_exists checks)
        while not self.update_thread_sentinel.is_set():
            try:
                if self.playing and pygame.mixer.music.get_busy():
                    pos_sec = pygame.mixer.music.get_pos()/1000.0
                    if hasattr(self,'current_time_label') and self.current_time_label.winfo_exists(): self.current_time_label.configure(text=self.format_time(pos_sec))
                    if self.current_song_duration_sec > 0:
                        prog = (pos_sec / self.current_song_duration_sec) * 100
                        if hasattr(self,'progress_slider') and self.progress_slider.winfo_exists(): self.progress_slider.set(prog)
                    elif hasattr(self,'progress_slider') and self.progress_slider.winfo_exists(): self.progress_slider.set(0)
                elif self.playing and not pygame.mixer.music.get_busy() and self.current_song_duration_sec > 0:
                    if self.playing: self.playing = False; 
                    if hasattr(self, 'after') and self.winfo_exists(): self.after(50, self.auto_play_next)
            except Exception as e:
                if not isinstance(e,(tkinter.TclError,RuntimeError, AttributeError)): print(f"Error in update_progress: {e}")
            time.sleep(0.2)

    def auto_play_next(self): # Unchanged
        if self.playlist_data and self.winfo_exists(): # Added winfo_exists
            if self.current_display_playlist_index < len(self.playlist_data)-1: self.next_song()
            else: self.stop_song()
    def on_closing(self): # Unchanged (with winfo_exists checks)
        print("Closing application...")
        self.update_thread_sentinel.set()
        if hasattr(self,'update_thread') and self.update_thread.is_alive(): self.update_thread.join(timeout=0.5)
        if hasattr(self, 'song_loading_dialog') and self.song_loading_dialog and self.song_loading_dialog.winfo_exists(): self.song_loading_dialog.destroy()
        if hasattr(self, 'generic_processing_dialog') and self.generic_processing_dialog and self.generic_processing_dialog.winfo_exists(): self.generic_processing_dialog.destroy()
        if pygame.mixer.get_init(): pygame.mixer.music.stop(); pygame.mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = MusicPlayerApp()
    app.mainloop()