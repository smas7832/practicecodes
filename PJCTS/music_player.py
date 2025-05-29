import os
import io
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
import threading
import time

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("800x500")
            
# what is valu
        self.bg_color = "#121212"
        self.fg_color = "#e0e0e0"
        self.accent_color = "#1DB954"  # Spotify green as accent
        self.secondary_bg = "#212121"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles for dark theme
        self.style = ttk.Style()
        self.style.configure("TScale", background=self.bg_color)
        self.style.configure("TButton", background=self.secondary_bg, foreground=self.fg_color)
        
        pygame.mixer.init()
        
        self.current_file = None
        self.paused = False
        self.current_time = 0
        self.total_time = 0
        self.updating = False
        
        self.create_ui()
        
    def create_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Album art frame
        self.art_frame = tk.Frame(self.main_frame, bg=self.bg_color, width=250, height=250)
        self.art_frame.pack(side=tk.LEFT, padx=10)
        self.art_frame.pack_propagate(False)
        
        # Default album art
        self.default_art = tk.PhotoImage(file="default_album.png") if os.path.exists("default_album.png") else None
        self.album_art_label = tk.Label(self.art_frame, bg=self.bg_color, image=self.default_art)
        self.album_art_label.pack(fill=tk.BOTH, expand=True)
        
        # Metadata and controls frame
        self.info_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Metadata labels
        self.title_label = tk.Label(self.info_frame, text="Title: Not Playing", bg=self.bg_color, fg=self.fg_color, 
                                   anchor="w", font=("Arial", 12, "bold"))
        self.title_label.pack(fill=tk.X, pady=5)
        
        self.artist_label = tk.Label(self.info_frame, text="Artist: -", bg=self.bg_color, fg=self.fg_color, 
                                    anchor="w", font=("Arial", 10))
        self.artist_label.pack(fill=tk.X, pady=2)
        
        self.album_label = tk.Label(self.info_frame, text="Album: -", bg=self.bg_color, fg=self.fg_color, 
                                   anchor="w", font=("Arial", 10))
        self.album_label.pack(fill=tk.X, pady=2)
        
        self.year_label = tk.Label(self.info_frame, text="Year: -", bg=self.bg_color, fg=self.fg_color, 
                                  anchor="w", font=("Arial", 10))
        self.year_label.pack(fill=tk.X, pady=2)
        
        # Progress bar
        self.progress_frame = tk.Frame(self.info_frame, bg=self.bg_color)
        self.progress_frame.pack(fill=tk.X, pady=15)
        
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        self.time_label = tk.Label(self.progress_frame, textvariable=self.time_var, bg=self.bg_color, fg=self.fg_color)
        self.time_label.pack(side=tk.BOTTOM, pady=5)
        
        self.progress_bar = ttk.Scale(self.progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.seek)
        self.progress_bar.pack(fill=tk.X)
        
        # Control buttons frame
        self.control_frame = tk.Frame(self.info_frame, bg=self.bg_color)
        self.control_frame.pack(pady=15)
        
        button_bg = self.secondary_bg
        button_fg = self.fg_color
        button_active_bg = self.accent_color
        button_active_fg = "#000000"
        
        self.select_btn = tk.Button(self.control_frame, text="Select File", command=self.select_file, width=10,
                                  bg=button_bg, fg=button_fg, activebackground=button_active_bg, 
                                  activeforeground=button_active_fg, relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.select_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = tk.Button(self.control_frame, text="Play", command=self.play_music, width=10,
                                bg=button_bg, fg=button_fg, activebackground=button_active_bg, 
                                activeforeground=button_active_fg, relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.play_btn.grid(row=0, column=1, padx=5)
        
        self.pause_btn = tk.Button(self.control_frame, text="Pause", command=self.pause_music, width=10,
                                 bg=button_bg, fg=button_fg, activebackground=button_active_bg, 
                                 activeforeground=button_active_fg, relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.pause_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = tk.Button(self.control_frame, text="Stop", command=self.stop_music, width=10,
                                bg=button_bg, fg=button_fg, activebackground=button_active_bg, 
                                activeforeground=button_active_fg, relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.stop_btn.grid(row=0, column=3, padx=5)
    
    def select_file(self):
        filetypes = (
            ("Audio files", "*.mp3 *.flac *.m4a *.wav"),
            ("All files", "*.*")
        )
        
        file_path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=filetypes
        )
        
        if file_path:
            self.current_file = file_path
            self.load_metadata(file_path)
            self.play_music()
    
    def load_metadata(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        
        title = os.path.basename(file_path)
        artist = "-"
        album = "-"
        year = "-"
        artwork = None
        
        try:
            if file_ext == '.mp3':
                audio = MP3(file_path)
                self.total_time = audio.info.length
                
                id3 = ID3(file_path)
                if 'TIT2' in id3:
                    title = id3['TIT2'].text[0]
                if 'TPE1' in id3:
                    artist = id3['TPE1'].text[0]
                if 'TALB' in id3:
                    album = id3['TALB'].text[0]
                if 'TDRC' in id3:
                    year = str(id3['TDRC'].text[0])
                
                # Extract album art
                for tag in id3.values():
                    if tag.FrameID == 'APIC':
                        artwork_data = tag.data
                        artwork = Image.open(io.BytesIO(artwork_data))
                        break
                        
            elif file_ext == '.flac':
                audio = FLAC(file_path)
                self.total_time = audio.info.length
                
                if 'title' in audio:
                    title = audio['title'][0]
                if 'artist' in audio:
                    artist = audio['artist'][0]
                if 'album' in audio:
                    album = audio['album'][0]
                if 'date' in audio:
                    year = audio['date'][0]
                
                # Extract album art from FLAC
                if audio.pictures:
                    artwork_data = audio.pictures[0].data
                    artwork = Image.open(io.BytesIO(artwork_data))
                    
            elif file_ext == '.m4a':
                audio = MP4(file_path)
                self.total_time = audio.info.length
                
                if '©nam' in audio:
                    title = audio['©nam'][0]
                if '©ART' in audio:
                    artist = audio['©ART'][0]
                if '©alb' in audio:
                    album = audio['©alb'][0]
                if '©day' in audio:
                    year = audio['©day'][0]
                
                # Extract album art from M4A
                if 'covr' in audio:
                    artwork_data = audio['covr'][0]
                    artwork = Image.open(io.BytesIO(artwork_data))
            
            else:
                # For WAV files or unsupported formats
                self.total_time = pygame.mixer.Sound(file_path).get_length()
        
        except Exception as e:
            print(f"Error loading metadata: {e}")
        
        # Update UI with metadata
        self.title_label.config(text=f"Title: {title}")
        self.artist_label.config(text=f"Artist: {artist}")
        self.album_label.config(text=f"Album: {album}")
        self.year_label.config(text=f"Year: {year}")
        
        # Display album art or default image
        if artwork:
            artwork = artwork.resize((250, 250), Image.LANCZOS)
            self.album_art = ImageTk.PhotoImage(artwork)
            self.album_art_label.config(image=self.album_art)
        else:
            self.album_art_label.config(image=self.default_art)
        
        # Format total time
        mins, secs = divmod(int(self.total_time), 60)
        self.time_var.set(f"00:00 / {mins:02d}:{secs:02d}")
    
    def play_music(self):
        if self.current_file:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            else:
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
                
                if not self.updating:
                    threading.Thread(target=self.update_progress, daemon=True).start()
                    self.updating = True
    
    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_time = 0
        self.progress_bar.set(0)
        mins, secs = divmod(int(self.total_time), 60)
        self.time_var.set(f"00:00 / {mins:02d}:{secs:02d}")
        self.paused = False
    
    def seek(self, value):
        if self.current_file and self.total_time > 0:
            position = float(value) / 100 * self.total_time
            pygame.mixer.music.set_pos(position)
            self.current_time = position
    
    def update_progress(self):
        while True:
            if self.current_file and pygame.mixer.music.get_busy() and not self.paused:
                self.current_time += 0.1
                if self.current_time > self.total_time:
                    self.current_time = 0
                    self.progress_bar.set(0)
                    continue
                
                # Update progress bar
                progress = (self.current_time / self.total_time) * 100
                self.progress_bar.set(progress)
                
                # Update time label
                current_mins, current_secs = divmod(int(self.current_time), 60)
                total_mins, total_secs = divmod(int(self.total_time), 60)
                self.time_var.set(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
            
            time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    
    # Create a dark-themed default album art image if it doesn't exist
    if not os.path.exists("default_album.png"):
        default_img = Image.new('RGB', (250, 250), color='#2a2a2a')
        default_img.save("default_album.png")
    
    root.mainloop()
