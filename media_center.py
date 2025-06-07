import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QStyle, QSlider, QMessageBox,
                             QListWidget, QListWidgetItem, QSizePolicy)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Center - XMB")
        self.setGeometry(100, 100, 1024, 768)  # Adjusted size for XMB

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main Vertical Layout (Categories on top, then item list and content area)
        super_main_v_layout = QVBoxLayout(central_widget)
        super_main_v_layout.setContentsMargins(0,0,0,0) # Use full window space
        super_main_v_layout.setSpacing(0)

        # --- Media Player Setup (MUST be before UI elements that use it) ---
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # self.video_widget is created later, output set after main_h_layout

        # --- Category List (Horizontal Top Bar) ---
        self.category_list_widget = QListWidget()
        self.category_list_widget.setObjectName("category_list_widget") # For QSS
        self.category_list_widget.setFlow(QListWidget.LeftToRight)
        self.category_list_widget.setFixedHeight(100) # Adjusted height
        # self.category_list_widget.setStyleSheet("QListWidget { background-color: #2c3e50; color: white; font-size: 18px; } QListWidget::item { padding: 10px; } QListWidget::item:selected { background-color: #e74c3c; }") # Will be replaced by global QSS
        self.category_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.category_list_widget.setFocusPolicy(Qt.StrongFocus)
        self.category_list_widget.setSelectionMode(QListWidget.SingleSelection)


        # --- XMB Data Structure ---
        self.xmb_data = {
            "Settings": ["Video Settings", "Audio Settings", "System Info", "Appearance"],
            "Music": ["/path/to/dummy/song1.mp3", "/path/to/dummy/song2.wav", "Open File..."],
            "Videos": ["/path/to/dummy/video1.mp4", "/path/to/dummy/video2.avi", "Open File..."],
            "Photos": ["All Photos", "Albums", "Date", "Slideshows"], # Photos not handled yet
            "Games": ["Game Launcher", "Installed Games"] # Placeholder
        }
        self.categories = list(self.xmb_data.keys())

        for cat_name in self.categories:
            item = QListWidgetItem(cat_name)
            item.setTextAlignment(Qt.AlignCenter) # Align text centrally
            self.category_list_widget.addItem(item)

        super_main_v_layout.addWidget(self.category_list_widget)

        # --- Playback Controls Bar ---
        playback_controls_layout = QHBoxLayout()

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.player.play)
        playback_controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pause_button.clicked.connect(self.player.pause)
        playback_controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.player.stop)
        playback_controls_layout.addWidget(self.stop_button)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        # self.volume_slider.setValue(self.player.volume()) # Set value after player is more fully initialized or connected
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        playback_controls_layout.addWidget(self.volume_slider)

        # playback_controls_layout.addStretch() # Optional: to push controls to one side

        super_main_v_layout.addLayout(playback_controls_layout) # Add control bar to main VBox

        # --- Main Content Area Layout (Item List on Left, Video Widget on Right) ---
        main_h_layout = QHBoxLayout()
        main_h_layout.setContentsMargins(0,0,0,0)
        main_h_layout.setSpacing(0)

        # --- Item List (Vertical Left Sidebar) ---
        self.item_list_widget = QListWidget()
        self.item_list_widget.setObjectName("item_list_widget") # For QSS
        self.item_list_widget.setFixedWidth(240) # Adjusted width
        # self.item_list_widget.setStyleSheet("QListWidget { background-color: #34495e; color: white; font-size: 16px; } QListWidget::item { padding: 8px; } QListWidget::item:selected { background-color: #c0392b; }") # Will be replaced by global QSS
        self.item_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.item_list_widget.setFocusPolicy(Qt.StrongFocus)
        self.item_list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Initial population will be handled by update_item_list via category change
        main_h_layout.addWidget(self.item_list_widget)

        # --- Video Widget (Main Content Display) ---
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("video_widget") # For QSS
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.video_widget.setStyleSheet("background-color: black;") # Will be replaced by global QSS
        main_h_layout.addWidget(self.video_widget, 1) # Add with stretch factor

        super_main_v_layout.addLayout(main_h_layout)
        central_widget.setLayout(super_main_v_layout)

        # --- Apply Global Stylesheet ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E; /* Dark grey background */
            }
            QListWidget {
                background-color: #1C1C1C; /* Very dark grey for lists */
                color: #E0E0E0; /* Light grey text, not pure white for less harshness */
                border: 1px solid #3A3A3A; /* Subtle border */
                font-size: 12pt; /* Adjusted font size */
                outline: none; /* Remove focus rectangle globally for lists */
            }
            QListWidget::item {
                padding: 10px; /* Spacing within items */
                border-bottom: 1px solid #282828; /* Separator for items */
            }
            QListWidget::item:selected {
                background-color: #0078D7; /* Blue highlight for selected item */
                color: #FFFFFF;
            }
            /* QListWidget::item:focus { outline: none; } */ /* Already part of QListWidget global */

            /* Style for the horizontal category list specifically */
            QListWidget#category_list_widget {
                border-top: none;
                border-left: none;
                border-right: none;
                border-bottom: 2px solid #4A4A4A; /* Prominent bottom border */
                font-size: 14pt; /* Larger font for categories */
            }
            QListWidget#category_list_widget::item {
                padding: 12px 18px; /* More padding for category items */
                margin: 0px 3px; /* Spacing between category items */
                border-bottom: none; /* No individual item separator */
            }
            QListWidget#category_list_widget::item:selected {
                background-color: #005A9E; /* Slightly different blue for category selection */
                border-radius: 4px; /* Rounded corners for selected category */
                color: #FFFFFF;
            }

            /* Style for the vertical item list */
            QListWidget#item_list_widget {
                border-top: none;
                border-bottom: none;
                border-left: none;
                border-right: 1px solid #3A3A3A; /* Separator from video widget */
            }
            QListWidget#item_list_widget::item {
                 padding-left: 15px; /* Indent item text a bit */
            }


            QPushButton {
                background-color: #4A4A4A;
                color: #E0E0E0;
                border: 1px solid #5A5A5A;
                padding: 6px 12px; /* Slightly more padding */
                min-height: 28px;
                border-radius: 3px; /* Subtle rounded corners */
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QPushButton:disabled {
                background-color: #333333; /* Darker for disabled */
                color: #666666; /* Lighter grey for disabled text */
            }
            QSlider {
                height: 20px; /* Ensure slider has enough vertical space for groove and handle */
            }
            QSlider::groove:horizontal {
                border: 1px solid #4A4A4A;
                height: 6px;
                background: #2A2A2A; /* Darker groove */
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078D7; /* Blue handle */
                border: 1px solid #005A9E;
                width: 16px; /* Slightly smaller handle */
                height: 16px; /* Make handle more substantial */
                margin: -5px 0; /* Adjust vertical margin to center */
                border-radius: 8px; /* Circular handle */
            }
            QVideoWidget#video_widget { /* Target by object name if needed, or globally */
                background-color: black;
            }
        """)

        # --- Media Player Signal Connections (after player and methods are defined) ---
        self.player.error.connect(self.handle_player_error)
        self.player.stateChanged.connect(self.update_playback_controls_state)
        self.player.mediaStatusChanged.connect(self.handle_media_status_changed)

        self.media_file_path = None

        # --- Connect Signals and Set Initial State ---
        self.category_list_widget.currentItemChanged.connect(self.update_item_list)
        if self.categories: # Ensure categories exist
            self.category_list_widget.setCurrentRow(0) # Select first category

        # Initial focus
        self.category_list_widget.setFocus()

        # Call manually once if currentItemChanged isn't triggered by setCurrentRow if no previous item
        if self.category_list_widget.currentItem():
             self.update_item_list(self.category_list_widget.currentItem(), None)

        # Initialize playback controls state after player is created
        self.update_playback_controls_state(self.player.state())
        self.handle_media_status_changed(self.player.mediaStatus())
        self.volume_slider.setValue(self.player.volume()) # Set initial volume slider value


    def update_playback_controls_state(self, state):
        if not hasattr(self, 'play_button'): # Controls might not be initialized yet
            return
        if state == QMediaPlayer.PlayingState:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        elif state == QMediaPlayer.PausedState:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif state == QMediaPlayer.StoppedState:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False) # Or True if stop should be active when media loaded but stopped

    def handle_media_status_changed(self, status):
        if not hasattr(self, 'play_button'): # Controls might not be initialized yet
            return
        # Enable/disable controls based on media presence
        if status == QMediaPlayer.LoadedMedia or status == QMediaPlayer.BufferedMedia or status == QMediaPlayer.BufferingMedia:
            # If player is stopped but media is loaded, play should be enabled.
            if self.player.state() == QMediaPlayer.StoppedState:
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(False) # Paused is false if stopped
                self.stop_button.setEnabled(True) # Stop is active if media is loaded
            # Other state updates are handled by update_playback_controls_state
            # Ensure volume slider is enabled
            self.volume_slider.setEnabled(True)
        elif status == QMediaPlayer.NoMedia or status == QMediaPlayer.InvalidMedia:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.volume_slider.setEnabled(False)
        elif status == QMediaPlayer.LoadingMedia: # Explicitly disable during loading
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.volume_slider.setEnabled(False)


    def update_item_list(self, current_category_item, previous_category_item):
        """Populates the item list based on the selected category."""
        if not current_category_item:
            return

        category_name = current_category_item.text()
        self.item_list_widget.clear()

        items_for_category = self.xmb_data.get(category_name, [])
        for item_name in items_for_category:
            self.item_list_widget.addItem(QListWidgetItem(item_name))

        if self.item_list_widget.count() > 0:
            self.item_list_widget.setCurrentRow(0)


    def keyPressEvent(self, event):
        key = event.key()
        current_focus = QApplication.focusWidget()

        if current_focus == self.category_list_widget:
            current_row = self.category_list_widget.currentRow()
            if key == Qt.Key_Right:
                self.category_list_widget.setCurrentRow((current_row + 1) % self.category_list_widget.count())
                event.accept()
            elif key == Qt.Key_Left:
                self.category_list_widget.setCurrentRow((current_row - 1 + self.category_list_widget.count()) % self.category_list_widget.count())
                event.accept()
            elif key in (Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter):
                if self.item_list_widget.count() > 0:
                    self.item_list_widget.setFocus()
                    self.item_list_widget.setCurrentRow(0) # Focus first item
                event.accept()
            else:
                super().keyPressEvent(event)

        elif current_focus == self.item_list_widget:
            current_row = self.item_list_widget.currentRow()
            if key == Qt.Key_Down:
                self.item_list_widget.setCurrentRow((current_row + 1) % self.item_list_widget.count())
                event.accept()
            elif key == Qt.Key_Up:
                self.item_list_widget.setCurrentRow((current_row - 1 + self.item_list_widget.count()) % self.item_list_widget.count())
                event.accept()
            elif key in (Qt.Key_Left, Qt.Key_Backspace):
                self.category_list_widget.setFocus()
                event.accept()
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                if self.item_list_widget.currentItem():
                    selected_item_text = self.item_list_widget.currentItem().text()
                    current_category_text = self.category_list_widget.currentItem().text()

                    if selected_item_text == "Open File...":
                        if current_category_text in ["Videos", "Music"]:
                            self.open_file_dialog()
                            print(f"Action: Opening file dialog for {current_category_text}.")
                        else:
                            print(f"'Open File...' selected under '{current_category_text}', not applicable here.")
                    elif current_category_text in ["Music", "Videos"]:
                        # This item is assumed to be a media file path
                        print(f"Attempting to play: {selected_item_text} under {current_category_text}")
                        media_content = QMediaContent(QUrl.fromLocalFile(selected_item_text))
                        self.player.setMedia(media_content)
                        self.player.play()
                    else:
                        # For other items like "Settings" items
                        print(f"Selected item: '{selected_item_text}' under '{current_category_text}' - No action defined yet.")
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Media File",
            "", # Default directory
            "Media Files (*.mp3 *.mp4 *.avi *.mkv *.wav);;All Files (*)", # Filter might change based on XMB context
            options=options
        )
        if file_path:
            self.media_file_path = file_path
            print(f"Selected file: {self.media_file_path}")
            media_content = QMediaContent(QUrl.fromLocalFile(self.media_file_path))
            self.player.setMedia(media_content)
            self.player.play() # Or update UI to show it's loaded

    def handle_player_error(self):
        error_string = self.player.errorString()
        print(f"Player Error: {error_string}")
        if error_string:
            QMessageBox.warning(self, "Media Player Error", error_string)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
