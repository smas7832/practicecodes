import sys
import os
import time
import threading
import re
import io

from PySide6.QtCore import (Qt, QUrl, QTimer, QThread, Signal, Slot, QStandardPaths, QSize, QPoint)
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction, QDesktopServices, QPainter, QColor, QBrush, QFontMetrics, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QProgressBar, QListWidget, QListWidgetItem,
    QFileDialog, QTextEdit, QSizePolicy, QStyle, QFrame, QSplitter, QMenu,
    QProgressDialog, QMessageBox
)
import pygame
from mutagen.mp3 import MP3, EasyMP3
from mutagen.id3 import ID3, APIC, USLT
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from PIL import Image as PILImage 
from PIL.ImageQt import ImageQt 

# --- Constants ---
DEFAULT_ALBUM_ART_PATH = "default_album_art_pyside.png" 
PLAYLIST_ITEM_THUMBNAIL_SIZE = QSize(48, 48) 
MAIN_ALBUM_ART_SIZE = QSize(200, 200)

# --- Helper for default album art (Unchanged) ---
def create_default_album_art_if_needed(path, size):
    if not os.path.exists(path):
        try:
            q_image = QImage(size, QImage.Format.Format_RGB32); q_image.fill(QColor(73,109,137))
            painter = QPainter(q_image); painter.setPen(Qt.GlobalColor.white)
            font = painter.font(); font.setPointSize(20); font.setBold(True); painter.setFont(font)
            painter.drawText(q_image.rect(), Qt.AlignmentFlag.AlignCenter, "No Art"); painter.end()
            q_image.save(path)
        except Exception as e: print(f"Error creating default Qt album art: {e}")

# --- SongLoaderThread (Unchanged) ---
class SongLoaderThread(QThread):
    progress_signal = Signal(int, int, str); song_data_signal = Signal(dict); finished_signal = Signal(list) 
    def __init__(self, filepaths_to_load, parent_app_ref):
        super().__init__(); self.filepaths_to_load = filepaths_to_load; self.app_ref = parent_app_ref 
    def run(self):
        all_data = []; total = len(self.filepaths_to_load)
        for i, path in enumerate(self.filepaths_to_load):
            if self.isInterruptionRequested(): return 
            self.progress_signal.emit(i + 1, total, os.path.basename(path))
            song_data = self.app_ref.get_song_metadata(path) 
            if song_data: self.song_data_signal.emit(song_data); all_data.append(song_data)
        if not self.isInterruptionRequested(): self.finished_signal.emit(all_data)

# --- Custom Widget for Playlist Items (Unchanged from previous fix) ---
class SongPlaylistItemWidget(QWidget):
    def __init__(self, song_data, default_thumb_pixmap, parent=None):
        super().__init__(parent); self.song_data = song_data; self.default_thumb_pixmap = default_thumb_pixmap; self.init_ui()
    def init_ui(self):
        layout=QHBoxLayout(self);layout.setContentsMargins(5,5,5,5);self.thumbnail_label=QLabel();self.thumbnail_label.setFixedSize(PLAYLIST_ITEM_THUMBNAIL_SIZE);self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_pix=self.song_data.get('playlist_thumbnail_qpixmap',self.default_thumb_pixmap)
        if thumb_pix: self.thumbnail_label.setPixmap(thumb_pix.scaled(PLAYLIST_ITEM_THUMBNAIL_SIZE,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.thumbnail_label);text_info_layout=QVBoxLayout();text_info_layout.setSpacing(2)
        self.title_label=QLabel(self.song_data.get('title','Unknown Title'));self.title_label.setStyleSheet("font-weight:bold;font-size:10pt;")
        artist=self.song_data.get('artist','Unknown Artist');album=self.song_data.get('album','')
        details=f"{artist}{f' - {album}'if album else''}";self.artist_album_label=QLabel(details);self.artist_album_label.setStyleSheet("font-size:8pt;color:#B0B0B0;")
        text_info_layout.addWidget(self.title_label);text_info_layout.addWidget(self.artist_album_label);text_info_layout.addStretch();layout.addLayout(text_info_layout,1)
        self.duration_label=QLabel(self.song_data.get('duration_str','--:--'));self.duration_label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter);self.duration_label.setStyleSheet("font-size:9pt;color:#A0A0A0;padding-right:5px;");self.duration_label.setFixedWidth(50);layout.addWidget(self.duration_label)
        self.setFixedHeight(PLAYLIST_ITEM_THUMBNAIL_SIZE.height()+10)
    def update_selection_style(self,is_selected,is_current_playing):
        base_title_style="font-weight:bold;font-size:10pt;";base_artist_style="font-size:8pt;color:#B0B0B0;"
        if is_current_playing:self.title_label.setStyleSheet(f"{base_title_style}color:#1E90FF;");self.artist_album_label.setStyleSheet(f"{base_artist_style}color:#6495ED;")
        elif is_selected:self.title_label.setStyleSheet(f"{base_title_style}color:white;");self.artist_album_label.setStyleSheet(f"{base_artist_style}color:#E0E0E0;")
        else:self.title_label.setStyleSheet(base_title_style);self.artist_album_label.setStyleSheet(base_artist_style)

# --- Main Application Window ---
class MusicPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Lyric Master Player Pro v1.5") 
        self.setGeometry(100, 100, 1200, 750) 
        pygame.mixer.init()

        self.playlist_data = []; self.original_song_paths_ordered = []
        self.metadata_cache = {} 
        self.current_song_playing_filepath = None; self.current_display_playlist_index = -1
        self.is_playing = False; self.is_paused = False; self.current_song_duration_sec = 0
        self.is_loading_songs_flag = False 
        self.lyrics_visible = False

        create_default_album_art_if_needed(DEFAULT_ALBUM_ART_PATH, MAIN_ALBUM_ART_SIZE)
        self.default_album_art_pixmap = QPixmap(DEFAULT_ALBUM_ART_PATH)
        self.default_playlist_item_thumb_pixmap = self._create_placeholder_thumbnail(PLAYLIST_ITEM_THUMBNAIL_SIZE, "♪")

        self._setup_ui()
        self._connect_signals()
        self.apply_stylesheet() 

        self.progress_update_timer = QTimer(self)
        self.progress_update_timer.setInterval(200) 
        self.progress_update_timer.timeout.connect(self.update_song_progress_display)

        self.current_song_loader_thread = None
        self.progress_dialog = None
        self.generic_processing_dialog = None

    def _pil_to_qpixmap(self, pil_image):
        try:
            if pil_image.mode != 'RGBA': pil_image = pil_image.convert('RGBA')
            qimage = ImageQt(pil_image)
            return QPixmap.fromImage(qimage)
        except Exception as e: print(f"Error converting PIL image to QPixmap: {e}"); return None

    def _create_placeholder_thumbnail(self,size,text=""): 
        q_image = QImage(size, QImage.Format.Format_ARGB32); q_image.fill(QColor(50,50,60))
        if text:
            painter=QPainter(q_image);painter.setPen(QColor(150,150,180));font=painter.font();font.setPointSize(size.height()//2);painter.setFont(font)
            painter.drawText(q_image.rect(),Qt.AlignmentFlag.AlignCenter,text);painter.end()
        return QPixmap.fromImage(q_image)

    def _setup_ui(self): # Unchanged from previous full code
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        top_info_frame = QFrame(); top_info_layout = QHBoxLayout(top_info_frame)
        self.album_art_label = QLabel(); self.album_art_label.setFixedSize(MAIN_ALBUM_ART_SIZE)
        self.album_art_label.setPixmap(self.default_album_art_pixmap.scaled(MAIN_ALBUM_ART_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter); top_info_layout.addWidget(self.album_art_label)
        song_details_layout = QVBoxLayout()
        self.song_title_label = QLabel("Song Title: N/A"); self.song_title_label.setObjectName("SongTitleLabel")
        self.artist_label = QLabel("Artist: N/A"); self.artist_label.setObjectName("ArtistLabel")
        self.album_year_label = QLabel("Album - Year: N/A"); self.album_year_label.setObjectName("AlbumYearLabel")
        song_details_layout.addWidget(self.song_title_label); song_details_layout.addWidget(self.artist_label); song_details_layout.addWidget(self.album_year_label); song_details_layout.addStretch(); top_info_layout.addLayout(song_details_layout)
        self.main_layout.addWidget(top_info_frame)
        progress_area_layout = QHBoxLayout(); self.current_time_label = QLabel("00:00")
        self.progress_slider = QSlider(Qt.Orientation.Horizontal); self.progress_slider.setRange(0,1000); self.progress_slider.setEnabled(False)
        self.total_time_label = QLabel("00:00"); progress_area_layout.addWidget(self.current_time_label); progress_area_layout.addWidget(self.progress_slider); progress_area_layout.addWidget(self.total_time_label)
        self.main_layout.addLayout(progress_area_layout)
        controls_layout = QHBoxLayout(); controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_button = QPushButton(); self.prev_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.play_pause_button = QPushButton(); self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)); self.play_pause_button.setObjectName("PlayPauseButton")
        self.stop_button = QPushButton(); self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.next_button = QPushButton(); self.next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        controls_layout.addWidget(self.prev_button); controls_layout.addWidget(self.play_pause_button); controls_layout.addWidget(self.stop_button); controls_layout.addWidget(self.next_button)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal); self.volume_slider.setRange(0,100); self.volume_slider.setValue(50); pygame.mixer.music.set_volume(0.5); self.volume_slider.setFixedWidth(150)
        volume_label = QLabel(); volume_label.setPixmap(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume).pixmap(QSize(24,24)))
        controls_layout.addStretch(); controls_layout.addWidget(volume_label); controls_layout.addWidget(self.volume_slider); self.main_layout.addLayout(controls_layout)
        self.middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.playlist_panel = QWidget(); playlist_panel_layout = QVBoxLayout(self.playlist_panel); playlist_panel_layout.setContentsMargins(0,0,0,0)
        playlist_header_layout = QHBoxLayout(); playlist_header_layout.addWidget(QLabel("Playlist")); playlist_header_layout.addStretch()
        self.sort_combo = QPushButton("Sort By: Added Order"); self.sort_combo.setFixedWidth(150); self.sort_menu_options = QMenu(self); self.sort_actions = {}
        sort_keys = ["Added Order","Title","Artist","Album","Year","Duration"]
        for key in sort_keys:
            action = QAction(key,self); action.setData(key); action.triggered.connect(self.handle_sort_action_triggered)
            self.sort_menu_options.addAction(action); self.sort_actions[key] = action
        self.sort_combo.setMenu(self.sort_menu_options); playlist_header_layout.addWidget(self.sort_combo); playlist_panel_layout.addLayout(playlist_header_layout)
        self.playlist_widget = QListWidget(); self.playlist_widget.setObjectName("PlaylistWidget"); self.playlist_widget.setAlternatingRowColors(True) 
        playlist_panel_layout.addWidget(self.playlist_widget)
        self.middle_splitter.addWidget(self.playlist_panel)
        self.lyrics_panel = QWidget(); lyrics_panel_layout = QVBoxLayout(self.lyrics_panel); lyrics_panel_layout.setContentsMargins(0,0,0,0)
        lyrics_header_layout = QHBoxLayout(); lyrics_header_layout.addWidget(QLabel("Lyrics")); lyrics_header_layout.addStretch()
        self.lyrics_toggle_button = QPushButton("Show Lyrics"); self.lyrics_toggle_button.setCheckable(True)
        lyrics_header_layout.addWidget(self.lyrics_toggle_button); lyrics_panel_layout.addLayout(lyrics_header_layout)
        self.lyrics_textbox = QTextEdit(); self.lyrics_textbox.setReadOnly(True); self.lyrics_textbox.setObjectName("LyricsTextbox"); lyrics_panel_layout.addWidget(self.lyrics_textbox)
        self.middle_splitter.addWidget(self.lyrics_panel); self.lyrics_panel.setVisible(False)
        initial_playlist_width = self.width() * 0.6 if self.width() > 600 else 400 
        self.middle_splitter.setSizes([int(initial_playlist_width) , int(self.width() - initial_playlist_width - 20) ]) 
        self.main_layout.addWidget(self.middle_splitter,1) 
        bottom_buttons_layout = QHBoxLayout(); self.load_file_button = QPushButton("Load File(s)"); self.load_folder_button = QPushButton("Load Folder")
        bottom_buttons_layout.addWidget(self.load_file_button); bottom_buttons_layout.addWidget(self.load_folder_button); bottom_buttons_layout.addStretch(); self.main_layout.addLayout(bottom_buttons_layout)
        self.handle_lyrics_toggled(False) 

    def _connect_signals(self): # Unchanged
        self.play_pause_button.clicked.connect(self.toggle_play_pause); self.stop_button.clicked.connect(self.stop_song)
        self.next_button.clicked.connect(self.next_song); self.prev_button.clicked.connect(self.prev_song)
        self.volume_slider.valueChanged.connect(self.set_volume); self.progress_slider.sliderMoved.connect(self.seek_song_from_slider_move)
        self.progress_slider.sliderReleased.connect(self.seek_song_from_slider_release)
        self.load_file_button.clicked.connect(self.handle_load_files); self.load_folder_button.clicked.connect(self.handle_load_folder)
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_from_playlist)
        self.playlist_widget.currentItemChanged.connect(self.handle_playlist_selection_changed)
        self.lyrics_toggle_button.toggled.connect(self.handle_lyrics_toggled)

    def apply_stylesheet(self): # Unchanged
        self.setStyleSheet("""
            QMainWindow { background-color: #2B2B2B; } QLabel { color: #D0D0D0; padding: 2px; }
            #SongTitleLabel { font-size: 18pt; font-weight: bold; color: #FFFFFF; }
            #ArtistLabel, #AlbumYearLabel { font-size: 11pt; color: #A0A0A0; }
            QPushButton { background-color: #4A4A4A; color: white; border: 1px solid #5A5A5A; padding: 8px; min-height: 20px; border-radius: 4px; }
            QPushButton:hover { background-color: #5A5A5A; } QPushButton:pressed { background-color: #3A3A3A; }
            QPushButton:checked { background-color: #1E90FF; border-color: #1C86EE;} 
            #PlayPauseButton { padding: 10px; }
            QSlider::groove:horizontal { border: 1px solid #5A5A5A; height: 8px; background: #3A3A3A; margin: 2px 0; border-radius: 4px; }
            QSlider::handle:horizontal { background: #1E90FF; border: 1px solid #1C86EE; width: 16px; margin: -4px 0; border-radius: 8px; }
            #PlaylistWidget { background-color: #333333; color: #E0E0E0; border: 1px solid #444444; font-size: 10pt; alternate-background-color: #3A3A3A;}
            #PlaylistWidget::item:selected { background-color: #1E90FF; /* color: white; ItemWidget controls its text color */ }
            #LyricsTextbox { background-color: #2E2E2E; color: #C0C0C0; border: 1px solid #444444; font-family: Consolas, monospace; font-size: 10pt; }
            QMenu { background-color: #4A4A4A; color: white; border: 1px solid #5A5A5A; } QMenu::item:selected { background-color: #1E90FF; }
            QSplitter::handle { background-color: #4A4A4A; } QSplitter::handle:horizontal { width: 5px; }
        """)
    
    def _center_popup(self, popup, width, height): # Unchanged
        if self.screen(): 
            screen_center = self.screen().geometry().center()
            x = screen_center.x() - (width // 2); y = screen_center.y() - (height // 2)
            popup.setGeometry(x, y, width, height)
        else: popup.setGeometry(300, 300, width, height)

    def _show_progress_dialog(self, title, label_text, max_value): # Unchanged
        if self.progress_dialog and self.progress_dialog.isVisible(): self.progress_dialog.cancel() 
        self.progress_dialog = QProgressDialog(label_text, "Cancel", 0, max_value, self)
        self.progress_dialog.setWindowTitle(title); self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True); self.progress_dialog.setAutoReset(True)
        self._center_popup(self.progress_dialog, 400, 120)
        self.is_loading_songs_flag = True; self._set_controls_enabled(False)
        return self.progress_dialog

    def _hide_progress_dialog(self): # Unchanged
        if self.progress_dialog and self.progress_dialog.isVisible(): self.progress_dialog.setValue(self.progress_dialog.maximum())
        self.progress_dialog = None; self.is_loading_songs_flag = False; self._set_controls_enabled(True)

    def _set_controls_enabled(self, enabled_state): # Unchanged
        widgets_to_toggle = [self.load_file_button, self.load_folder_button, self.sort_combo, self.lyrics_toggle_button,
                             self.prev_button, self.play_pause_button, self.stop_button, self.next_button, self.volume_slider]
        for widget in widgets_to_toggle:
            if hasattr(widget, 'isEnabled') and hasattr(widget, 'setEnabled'):
                 widget.setEnabled(enabled_state)
        if hasattr(self, 'progress_slider'):
            self.progress_slider.setEnabled(enabled_state and self.current_song_playing_filepath is not None)

    def show_generic_processing_dialog(self, message="Processing..."): # Unchanged
        if self.generic_processing_dialog and self.generic_processing_dialog.isVisible():self.generic_processing_dialog.close(); self.generic_processing_dialog.deleteLater()
        self.generic_processing_dialog=QMessageBox(self); self.generic_processing_dialog.setWindowTitle("Processing")
        self.generic_processing_dialog.setText(message); self.generic_processing_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        self.generic_processing_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._center_popup(self.generic_processing_dialog,300,100)
        self.generic_processing_dialog.show()
    def hide_generic_processing_dialog(self): # Unchanged
        if self.generic_processing_dialog and self.generic_processing_dialog.isVisible():self.generic_processing_dialog.close(); self.generic_processing_dialog.deleteLater()
        self.generic_processing_dialog=None

    def get_song_metadata(self, song_path): # This is the corrected version from previous detailed explanation
        if song_path in self.metadata_cache:
            cached_data = self.metadata_cache[song_path].copy()
            if cached_data.get('lyrics') is None: 
                lrc_path = os.path.splitext(song_path)[0] + ".lrc"
                lrc_lyrics = self._parse_lrc_file(lrc_path)
                if lrc_lyrics:
                    cached_data['lyrics'] = lrc_lyrics
                    self.metadata_cache[song_path]['lyrics'] = lrc_lyrics
            if 'playlist_thumbnail_qpixmap' not in cached_data or cached_data['playlist_thumbnail_qpixmap'] is None:
                if cached_data.get('album_art_qpixmap'):
                    cached_data['playlist_thumbnail_qpixmap'] = cached_data['album_art_qpixmap'].scaled(
                        PLAYLIST_ITEM_THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )
                else:
                    cached_data['playlist_thumbnail_qpixmap'] = self.default_playlist_item_thumb_pixmap
                self.metadata_cache[song_path]['playlist_thumbnail_qpixmap'] = cached_data['playlist_thumbnail_qpixmap']
            return cached_data

        filename = os.path.basename(song_path)
        song_data = {'filepath':song_path,'title':filename,'artist':"Unknown Artist",'album':"Unknown Album",'year':"",'duration_sec':0,'duration_str':"00:00",'album_art_qpixmap':None, 'playlist_thumbnail_qpixmap': None, 'lyrics': None}
        pil_image = None 
        try:
            ext = os.path.splitext(song_path)[1].lower()
            if ext == ".mp3":
                audio_tags=None; audio_easy=None
                try: audio_tags=ID3(song_path)
                except: pass # Fail silently for tags
                try: audio_easy=EasyMP3(song_path)
                except: pass
                if audio_easy:
                    if 'title' in audio_easy: song_data['title']=audio_easy['title'][0]
                    if 'artist' in audio_easy: song_data['artist']=audio_easy['artist'][0]
                    if 'album' in audio_easy: song_data['album']=audio_easy['album'][0]
                    if 'date' in audio_easy and audio_easy['date']: song_data['year']=audio_easy['date'][0][:4]
                if audio_tags:
                    for key in audio_tags.keys(): # Check for USLT lyrics tag
                        if key.startswith('USLT'): song_data['lyrics'] = audio_tags[key].text; break
                    for tag_val in audio_tags.values(): # Album art
                        if isinstance(tag_val,APIC): pil_image = PILImage.open(io.BytesIO(tag_val.data)); break
                try: # Duration for MP3
                    audio_duration_info = MP3(song_path); song_data['duration_sec'] = audio_duration_info.info.length
                except: pass 
            elif ext == ".flac":
                audio_flac = FLAC(song_path)
                if audio_flac:
                    if 'title' in audio_flac: song_data['title'] = audio_flac['title'][0]
                    if 'artist' in audio_flac: song_data['artist'] = audio_flac['artist'][0]
                    if 'album' in audio_flac: song_data['album'] = audio_flac['album'][0]
                    if 'date' in audio_flac and audio_flac['date']: song_data['year'] = audio_flac['date'][0][:4]
                    for key in ['lyrics', 'LYRICS', 'UNSYNCEDLYRICS']: # Check common FLAC lyric tags
                        if key in audio_flac: song_data['lyrics'] = audio_flac[key][0]; break
                    if audio_flac.pictures: pil_image = PILImage.open(io.BytesIO(audio_flac.pictures[0].data))
                    if hasattr(audio_flac, 'info'): song_data['duration_sec'] = audio_flac.info.length
            elif ext == ".ogg":
                audio_ogg = OggVorbis(song_path)
                if audio_ogg:
                    if 'title' in audio_ogg: song_data['title'] = audio_ogg['title'][0]
                    if 'artist' in audio_ogg: song_data['artist'] = audio_ogg['artist'][0]
                    if 'album' in audio_ogg: song_data['album'] = audio_ogg['album'][0]
                    if 'date' in audio_ogg and audio_ogg['date']: song_data['year'] = audio_ogg['date'][0][:4]
                    if 'lyrics' in audio_ogg: song_data['lyrics'] = audio_ogg['lyrics'][0] 
                    if hasattr(audio_ogg, 'info'): song_data['duration_sec'] = audio_ogg.info.length
            
            if song_data['duration_sec'] == 0 and os.path.exists(song_path): # Pygame fallback for duration
                try: temp_sound=pygame.mixer.Sound(song_path);song_data['duration_sec']=temp_sound.get_length();del temp_sound
                except pygame.error: print(f"Pygame could not get duration for {filename}")
            
            if song_data['duration_sec']>0: song_data['duration_str']=self.format_time(song_data['duration_sec'])
            if pil_image: 
                song_data['album_art_qpixmap'] = self._pil_to_qpixmap(pil_image)
                if song_data['album_art_qpixmap']:
                    song_data['playlist_thumbnail_qpixmap'] = song_data['album_art_qpixmap'].scaled(
                        PLAYLIST_ITEM_THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )
            if not song_data.get('playlist_thumbnail_qpixmap'): # If no album art, use default placeholder for playlist
                song_data['playlist_thumbnail_qpixmap'] = self.default_playlist_item_thumb_pixmap

        except Exception as e_meta: print(f"Meta error for {filename}: {e_meta}")
        
        # Fallback to .lrc file if no embedded lyrics found
        if song_data.get('lyrics') is None:
            lrc_filepath = os.path.splitext(song_path)[0] + ".lrc"
            song_data['lyrics'] = self._parse_lrc_file(lrc_filepath)
        
        self.metadata_cache[song_path] = song_data.copy() 
        return song_data.copy()

    def _parse_lrc_file(self, lrc_filepath):
        lyrics_lines = [];
        try:
            with open(lrc_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    line_text = re.sub(r'\[[0-9]{2}:[0-9]{2}\.[0-9]{2,3}\]', '', line)
                    line_text = re.sub(r'\[[a-zA-Z]{2,}:.*?\]', '', line_text) 
                    if line_text: lyrics_lines.append(line_text)
            return "\n".join(lyrics_lines) if lyrics_lines else None
        except FileNotFoundError: return None
        except Exception as e: print(f"LRC Parse Error {os.path.basename(lrc_filepath)}: {e}"); return None

    def _start_song_loading_thread(self, filepaths):
        self.progress_dialog = self._show_progress_dialog("Loading Songs", "Scanning files...", len(filepaths))
        self.current_song_loader_thread = SongLoaderThread(filepaths, self)
        self.current_song_loader_thread.progress_signal.connect(self._update_loading_progress_dialog)
        self.current_song_loader_thread.song_data_signal.connect(self._add_single_song_to_internal_list) 
        self.current_song_loader_thread.finished_signal.connect(self._finalize_song_loading_from_thread)
        if self.progress_dialog: self.progress_dialog.canceled.connect(self.current_song_loader_thread.requestInterruption) 
        self.current_song_loader_thread.start()

    @Slot(int, int, str)
    def _update_loading_progress_dialog(self, current, total, filename):
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.setLabelText(f"Processing: {filename} ({current}/{total})")
            self.progress_dialog.setValue(current)

    @Slot(dict)
    def _add_single_song_to_internal_list(self, song_data):
        if not any(orig_path == song_data['filepath'] for orig_path in self.original_song_paths_ordered):
            self.original_song_paths_ordered.append(song_data['filepath'])
        found_in_playlist = False
        for i, existing_sd in enumerate(self.playlist_data):
            if existing_sd['filepath'] == song_data['filepath']:
                self.playlist_data[i] = song_data; found_in_playlist = True; break
        if not found_in_playlist: self.playlist_data.append(song_data)

    @Slot(list)
    def _finalize_song_loading_from_thread(self, all_processed_song_data_in_batch):
        self._hide_progress_dialog()
        if self.current_song_loader_thread and self.current_song_loader_thread.isInterruptionRequested():
            print("Loading cancelled."); self.current_song_loader_thread = None; return
        if all_processed_song_data_in_batch or not self.playlist_widget.count(): 
            self.sort_playlist(self.get_current_sort_key(), use_dialog=False) 
            if not self.is_playing and not self.is_paused and self.playlist_data:
                first_path = all_processed_song_data_in_batch[0]['filepath'] if all_processed_song_data_in_batch else None
                if first_path:
                    try: idx = next(i for i,d in enumerate(self.playlist_data) if d['filepath']==first_path); self.play_song_by_display_index(idx)
                    except StopIteration:
                        if self.playlist_data: self.play_song_by_display_index(0)
                elif self.playlist_data: self.play_song_by_display_index(0)
        self.current_song_loader_thread = None

    def handle_load_files(self):
        if self.is_loading_songs_flag: QMessageBox.information(self, "Busy", "Loading in progress."); return
        paths,_ = QFileDialog.getOpenFileNames(self,"Select Audio",QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation),"Audio (*.mp3 *.flac *.ogg *.wav)")
        if paths: self._start_song_loading_thread(paths)

    def handle_load_folder(self):
        if self.is_loading_songs_flag: QMessageBox.information(self, "Busy", "Loading in progress."); return
        folder = QFileDialog.getExistingDirectory(self,"Select Folder",QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation))
        if folder:
            paths = []
            for r,_,fs in os.walk(folder):
                for f_name in fs:
                    if f_name.lower().endswith((".mp3",".flac",".ogg",".wav")): paths.append(os.path.join(r,f_name))
            if paths: self._start_song_loading_thread(paths)
            else: QMessageBox.information(self,"No Songs","No compatible audio files found.")
    
    def repopulate_playlist_widget(self):
        if not (hasattr(self, 'playlist_widget') and self.playlist_widget.isVisible()): return
        self.playlist_widget.clear()
        if not self.playlist_data: 
            placeholder_item = QListWidgetItem(self.playlist_widget)
            label = QLabel("Playlist is empty. Load some songs!")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
            placeholder_item.setSizeHint(label.sizeHint())
            self.playlist_widget.addItem(placeholder_item)
            self.playlist_widget.setItemWidget(placeholder_item, label)
            return

        for i, song_data in enumerate(self.playlist_data):
            list_item = QListWidgetItem(self.playlist_widget) 
            list_item.setData(Qt.ItemDataRole.UserRole, song_data['filepath']) 
            item_widget = SongPlaylistItemWidget(song_data, self.default_playlist_item_thumb_pixmap)
            list_item.setSizeHint(item_widget.sizeHint()) 
            self.playlist_widget.addItem(list_item) 
            self.playlist_widget.setItemWidget(list_item, item_widget) 
        self.update_current_playlist_item_highlight_in_widget()

    def update_current_playlist_item_highlight_in_widget(self):
        if not (hasattr(self, 'playlist_widget') and self.playlist_widget.isVisible()): return
        for row in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(row)
            if not item: continue 
            widget = self.playlist_widget.itemWidget(item)
            if isinstance(widget, SongPlaylistItemWidget):
                is_selected = (self.playlist_widget.currentRow() == row)
                is_playing_this = (self.current_display_playlist_index == row and (self.is_playing or self.is_paused))
                widget.update_selection_style(is_selected, is_playing_this)

        if self.current_display_playlist_index != -1 and self.current_display_playlist_index < self.playlist_widget.count():
            self.playlist_widget.setCurrentRow(self.current_display_playlist_index)
            item = self.playlist_widget.item(self.current_display_playlist_index)
            if item: self.playlist_widget.scrollToItem(item, QListWidget.ScrollHint.EnsureVisible)
        else:
            self.playlist_widget.setCurrentRow(-1)

    @Slot(QListWidgetItem, QListWidgetItem) 
    def handle_playlist_selection_changed(self, current_item, previous_item):
        if previous_item:
            widget = self.playlist_widget.itemWidget(previous_item)
            if isinstance(widget, SongPlaylistItemWidget): widget.update_selection_style(False, False) 
        if current_item:
            widget = self.playlist_widget.itemWidget(current_item)
            if isinstance(widget, SongPlaylistItemWidget):
                is_playing_this = (self.current_display_playlist_index == self.playlist_widget.row(current_item) and (self.is_playing or self.is_paused))
                widget.update_selection_style(True, is_playing_this)

    @Slot(QListWidgetItem)
    def play_selected_from_playlist(self, item):
        if item:
            song_filepath = item.data(Qt.ItemDataRole.UserRole)
            try:
                idx = next(i for i, data in enumerate(self.playlist_data) if data['filepath'] == song_filepath)
                self.play_song_by_display_index(idx)
            except StopIteration: print(f"Error: Song {song_filepath} not found in internal list.")

    def get_current_sort_key(self):
        if hasattr(self, 'sort_combo'): return self.sort_combo.text().replace("Sort By: ", "")
        return "Added Order" 
    @Slot()
    def handle_sort_action_triggered(self):
        action = self.sender(); 
        if action: sort_key = action.data(); self.sort_combo.setText(f"Sort By: {sort_key}"); self.sort_playlist_with_dialog(sort_key)
    
    def sort_playlist_with_dialog(self, sort_key):
        self.show_generic_processing_dialog(f"Sorting by {sort_key}...")
        QTimer.singleShot(10, lambda: self._perform_sort_and_hide_dialog(sort_key))

    def _perform_sort_and_hide_dialog(self, sort_key):
        self.sort_playlist(sort_key) 
        self.hide_generic_processing_dialog()

    def sort_playlist(self, sort_key, use_dialog=False): # use_dialog is for symmetry, not used for action
        if self.is_loading_songs_flag: return
        current_playing_path = self.current_song_playing_filepath
        def safe_lower(s_val): return (s_val or "").lower()
        def safe_year_key(s_item): year_val = s_item.get('year','0000'); return year_val if year_val else '0000'
        if sort_key=="Added Order":
            temp_map={d['filepath']:d for d in self.playlist_data}
            self.playlist_data=[temp_map[p] for p in self.original_song_paths_ordered if p in temp_map]
        elif sort_key=="Title":self.playlist_data.sort(key=lambda s:safe_lower(s.get('title')))
        elif sort_key=="Artist":self.playlist_data.sort(key=lambda s:safe_lower(s.get('artist')))
        elif sort_key=="Album":self.playlist_data.sort(key=lambda s:safe_lower(s.get('album')))
        elif sort_key=="Year":self.playlist_data.sort(key=safe_year_key) # Corrected call
        elif sort_key=="Duration":self.playlist_data.sort(key=lambda s:s.get('duration_sec',0))
        if current_playing_path:
            try:self.current_display_playlist_index=next(i for i,d in enumerate(self.playlist_data)if d['filepath']==current_playing_path)
            except StopIteration:self.current_display_playlist_index=-1
        elif self.playlist_data:self.current_display_playlist_index=0
        else:self.current_display_playlist_index=-1
        if hasattr(self, 'repopulate_playlist_widget'): self.repopulate_playlist_widget()

    @Slot(bool)
    def handle_lyrics_toggled(self, checked):
        self.lyrics_visible = checked; 
        self.lyrics_panel.setVisible(checked)
        self.lyrics_toggle_button.setText("Hide Lyrics" if checked else "Show Lyrics")
        current_sizes = self.middle_splitter.sizes()
        total_valid_width = sum(s for s in current_sizes if s >= 0) 
        if total_valid_width <= 10 and self.middle_splitter.isVisible(): total_valid_width = self.middle_splitter.width() 
        if checked: 
            playlist_w = total_valid_width * 0.6 
            lyrics_w = total_valid_width * 0.4  
            if playlist_w < 200 and total_valid_width > 300: playlist_w = 200; lyrics_w = total_valid_width - 200
            if lyrics_w < 150 and total_valid_width > 300: lyrics_w = 150; playlist_w = total_valid_width - 150
            self.middle_splitter.setSizes([int(max(100, playlist_w)), int(max(100, lyrics_w))])
            self.update_lyrics_display_content() 
        else: 
            self.middle_splitter.setSizes([max(1, total_valid_width), 0])

    def update_lyrics_display_content(self): # This is the critical display update
        if not hasattr(self, 'lyrics_textbox') or not self.lyrics_textbox.isVisible(): 
            if self.lyrics_visible: print("Lyrics textbox not visible but should be.") # Debug
            return
        
        lyrics_text = "Lyrics not available for this song."
        if self.current_display_playlist_index != -1 and self.current_display_playlist_index < len(self.playlist_data):
            # Ensure playlist_data is accessed correctly
            current_song_data = self.playlist_data[self.current_display_playlist_index]
            if current_song_data and current_song_data.get('lyrics'): # Check if song_data and lyrics exist
                lyrics_text = current_song_data['lyrics']
        
        self.lyrics_textbox.setPlainText(lyrics_text)


    @Slot()
    def toggle_play_pause(self):
        if not self.playlist_data:return
        if self.is_playing:
            pygame.mixer.music.pause(); self.is_paused=True; self.is_playing=False
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)); self.progress_update_timer.stop()
        elif self.is_paused:
            pygame.mixer.music.unpause(); self.is_paused=False; self.is_playing=True
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)); self.progress_update_timer.start()
        else: 
            idx_to_play = self.current_display_playlist_index if self.current_display_playlist_index!=-1 else 0
            if self.playlist_data: self.play_song_by_display_index(idx_to_play)

    def play_song_by_display_index(self, display_index):
        if not (0 <= display_index < len(self.playlist_data)): self.stop_song(); return
        self.current_display_playlist_index = display_index
        song_data = self.playlist_data[display_index].copy() 
        self.current_song_playing_filepath = song_data['filepath']
        self.current_song_duration_sec = song_data.get('duration_sec', 0)
        try:
            pygame.mixer.music.load(self.current_song_playing_filepath); pygame.mixer.music.play()
            self.is_playing = True; self.is_paused = False
            if hasattr(self,'play_pause_button') and self.play_pause_button.isEnabled(): self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            if hasattr(self,'progress_slider'): self.progress_slider.setEnabled(True); 
            self.progress_update_timer.start()
            self._update_main_song_info_display(song_data)
            self.update_current_playlist_item_highlight_in_widget()
            self.update_lyrics_display_content() # Ensure lyrics are updated
        except pygame.error as e:
            print(f"Error playing {self.current_song_playing_filepath}: {e}")
            if hasattr(self,'song_title_label'): self.song_title_label.setText("Error playing song.")
            self.is_playing=False; self.is_paused=False
            if hasattr(self,'play_pause_button'): self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            if hasattr(self,'progress_update_timer'): self.progress_update_timer.stop()

    def _update_main_song_info_display(self, song_data):
        if not hasattr(self, 'song_title_label') or not self.song_title_label.isVisible(): return 
        self.song_title_label.setText(f"{song_data.get('title','N/A')}")
        self.artist_label.setText(f"{song_data.get('artist','N/A')}")
        ay = f"{song_data.get('album','N/A')}{' - '+song_data.get('year') if song_data.get('year') else ''}"; self.album_year_label.setText(ay)
        art_px = song_data.get('album_art_qpixmap') or self.default_album_art_pixmap
        self.album_art_label.setPixmap(art_px.scaled(MAIN_ALBUM_ART_SIZE,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        self.total_time_label.setText(self.format_time(self.current_song_duration_sec))
        self.progress_slider.setRange(0,int(self.current_song_duration_sec*1000)); self.progress_slider.setValue(0)

    @Slot()
    def stop_song(self):
        pygame.mixer.music.stop(); self.is_playing=False; self.is_paused=False; self.current_song_playing_filepath=None
        if hasattr(self,'play_pause_button'): self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        if hasattr(self,'progress_update_timer'): self.progress_update_timer.stop()
        if hasattr(self,'progress_slider'): self.progress_slider.setValue(0); self.progress_slider.setEnabled(False)
        if hasattr(self,'current_time_label'): self.current_time_label.setText("00:00")
        self.update_lyrics_display_content() # Clear or set default lyrics
        self.update_current_playlist_item_highlight_in_widget() 

    @Slot()
    def next_song(self):
        if not self.playlist_data:return;idx=0 if self.current_display_playlist_index==-1 else (self.current_display_playlist_index+1)%len(self.playlist_data);self.play_song_by_display_index(idx)
    @Slot()
    def prev_song(self):
        if not self.playlist_data:return;idx=len(self.playlist_data)-1 if self.current_display_playlist_index==-1 else (self.current_display_playlist_index-1+len(self.playlist_data))%len(self.playlist_data);self.play_song_by_display_index(idx)
    @Slot(int)
    def set_volume(self, value): pygame.mixer.music.set_volume(value / 100.0)

    _slider_pressed = False 
    @Slot(int)
    def seek_song_from_slider_move(self, value_ms):
        MusicPlayerWindow._slider_pressed=True
        if hasattr(self,'current_time_label'): self.current_time_label.setText(self.format_time(value_ms/1000.0))
        if hasattr(self,'progress_update_timer') and self.progress_update_timer.isActive(): self.progress_update_timer.stop()
    @Slot()
    def seek_song_from_slider_release(self):
        if MusicPlayerWindow._slider_pressed:
            value_ms=self.progress_slider.value(); seek_s=value_ms/1000.0
            if self.is_playing or self.is_paused: 
                try: pygame.mixer.music.set_pos(seek_s); 
                except pygame.error: pygame.mixer.music.play(start=seek_s) 
                if self.is_paused: pygame.mixer.music.unpause() 
            self.is_playing=True; self.is_paused=False 
            if hasattr(self,'play_pause_button'): self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            if hasattr(self,'progress_update_timer'): self.progress_update_timer.start()
        MusicPlayerWindow._slider_pressed=False

    @Slot()
    def update_song_progress_display(self):
        if self.is_playing and not MusicPlayerWindow._slider_pressed:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms == -1 and self.is_playing: 
                if hasattr(self,'progress_update_timer'): self.progress_update_timer.stop()
                self.is_playing=False; 
                if hasattr(self, 'auto_play_next') and self.isVisible(): self.auto_play_next() 
                return
            if pos_ms != -1 : 
                if hasattr(self,'current_time_label') and self.current_time_label.isVisible(): self.current_time_label.setText(self.format_time(pos_ms/1000.0))
                if hasattr(self,'progress_slider') and self.progress_slider.isEnabled(): self.progress_slider.setValue(pos_ms)
        elif not self.is_playing and not self.is_paused and not MusicPlayerWindow._slider_pressed: 
            if hasattr(self,'progress_update_timer'): self.progress_update_timer.stop()

    def auto_play_next(self):
        if self.playlist_data and self.current_display_playlist_index!=-1 and self.isVisible(): 
            if self.current_display_playlist_index < len(self.playlist_data)-1: self.next_song()
            else: self.stop_song(); self.current_display_playlist_index=0; self.update_current_playlist_item_highlight_in_widget()

    def format_time(self, seconds_float):
        s=int(seconds_float);m=s//60;s%=60;return f"{m:02d}:{s:02d}"
    
    def closeEvent(self, event):
        print("Closing application...")
        if self.current_song_loader_thread and self.current_song_loader_thread.isRunning():
            reply = QMessageBox.question(self,'Confirm Exit',"Loading in progress. Exit anyway?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: event.ignore(); return
            else: self.current_song_loader_thread.requestInterruption(); self.current_song_loader_thread.wait(500)
        if hasattr(self, 'progress_update_timer') and self.progress_update_timer.isActive(): self.progress_update_timer.stop()
        if pygame.mixer.get_init(): pygame.mixer.music.stop(); pygame.mixer.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    player_window = MusicPlayerWindow()
    player_window.show()
    sys.exit(app.exec())