import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QStyle, QSlider, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Center")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Video Widget
        self.video_widget = QVideoWidget()
        main_layout.addWidget(self.video_widget)

        # Media Player
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        self.player.error.connect(self.handle_player_error)

        # Controls Layout
        controls_layout = QHBoxLayout()

        # Play Button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.player.play)
        controls_layout.addWidget(self.play_button)

        # Pause Button
        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pause_button.clicked.connect(self.player.pause)
        controls_layout.addWidget(self.pause_button)

        # Stop Button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.player.stop)
        controls_layout.addWidget(self.stop_button)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.player.volume()) # Initial volume
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        controls_layout.addWidget(self.volume_slider)

        # Open File Button - moved into controls layout
        self.open_button = QPushButton("Open File", self)
        self.open_button.clicked.connect(self.open_file_dialog)
        controls_layout.addWidget(self.open_button)

        main_layout.addLayout(controls_layout)

        central_widget.setLayout(main_layout)
        self.media_file_path = None

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Media File",
            "", # Default directory
            "Media Files (*.mp3 *.mp4 *.avi *.mkv *.wav);;All Files (*)",
            options=options
        )
        if file_path:
            self.media_file_path = file_path
            print(f"Selected file: {self.media_file_path}")
            media_content = QMediaContent(QUrl.fromLocalFile(self.media_file_path))
            self.player.setMedia(media_content)
            # self.player.play() # Removed auto-play

    def handle_player_error(self):
        error_string = self.player.errorString()
        print(f"Player Error: {error_string}")
        if error_string: # QMediaPlayer might emit error signal with empty string initially
            QMessageBox.warning(self, "Media Player Error", error_string)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
