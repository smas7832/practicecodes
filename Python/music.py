import sys
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtMultimedia, QtMultimediaWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)

        layout = QtWidgets.QVBoxLayout(main_widget)

        self.playlist_widget = QtWidgets.QListWidget()
        layout.addWidget(self.playlist_widget)

        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)

        self.play_button = QtWidgets.QPushButton("Play")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.stop_button = QtWidgets.QPushButton("Stop")

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)

        layout.addWidget(controls)

        self.media_player = QtMultimedia.QMediaPlayer()

        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.media_player.pause)
        self.stop_button.clicked.connect(self.media_player.stop)
        self.load_music()
    def load_music(self):
        directory = Path("music")
        for file in directory.glob("*.mp3"):
            self.playlist_widget.addItem(str(file))

        settings = QtCore.QSettings()
        settings.setValue("last_music_folder", str(directory))

    def play(self):
        current_item = self.playlist_widget.currentItem()
        if current_item:
            url = QtCore.QUrl.fromLocalFile(current_item.text())
            content = QtMultimedia.QMediaContent(url)
            self.media_player.setMedia(content)
            self.media_player.play()
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
