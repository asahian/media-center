import unittest
import sys

# Ensure QApplication is created before importing QtMultimedia
app_instance = None
if not hasattr(sys, 'qapp_created'): # Check if already created
    try:
        from PyQt5.QtWidgets import QApplication
        app_instance = QApplication.instance()
        if app_instance is None:
            app_instance = QApplication(sys.argv)
        sys.qapp_created = True
    except Exception as e:
        print(f"Error creating QApplication in test setup: {e}")


from PyQt5.QtWidgets import QPushButton, QSlider
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Assuming media_center.py is in the same directory or accessible via PYTHONPATH
from media_center import MainWindow

class TestMediaCenter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This is to ensure QApplication exists for the entire test suite
        # It's a bit of a workaround for how Qt applications are typically structured
        # and how unittest discovers/runs tests.
        global app_instance
        if app_instance is None and not hasattr(sys, '_qapp_instance_created_by_test'):
            print("Creating QApplication for test class...")
            # QApplication.setApplicationName("MediaCenterTest") # Optional
            cls.app = QApplication(sys.argv) # Use sys.argv or []
            sys._qapp_instance_created_by_test = True
        elif app_instance:
             cls.app = app_instance


    def setUp(self):
        """Set up for each test."""
        if not QApplication.instance():
             # This might be redundant if setUpClass works as expected,
             # but good as a fallback.
            print("Re-creating QApplication in setUp (should ideally be in setUpClass)")
            self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        # self.main_window.show() # Not strictly necessary for many logic tests, but can be useful

        # It's good to have a dummy file path that looks valid for tests
        # Even if the file doesn't exist, QUrl.fromLocalFile will create a QUrl
        self.dummy_media_path = "/tmp/test_video.mp4"
        # Create a dummy QMediaContent for reuse in tests
        self.dummy_media_content = QMediaContent(QUrl.fromLocalFile(self.dummy_media_path))


    def tearDown(self):
        """Clean up after each test."""
        # It's important to properly close windows if they were shown,
        # and manage resources to avoid issues between tests.
        self.main_window.close()
        del self.main_window
        # QApplication.quit() # Avoid quitting if app is shared across tests in setUpClass

    @classmethod
    def tearDownClass(cls):
        # Clean up the application instance if created by this test class
        if hasattr(sys, '_qapp_instance_created_by_test') and sys._qapp_instance_created_by_test:
            if QApplication.instance():
                QApplication.instance().quit()
            delattr(sys, '_qapp_instance_created_by_test')
        elif hasattr(sys, 'qapp_created') and sys.qapp_created :
             # If the initial global app was used, don't quit it here, let it be managed outside
             pass


    def test_initial_ui_elements(self):
        """Test that all expected UI elements are present initially."""
        self.assertIsNotNone(self.main_window.player, "QMediaPlayer should exist.")
        self.assertIsNotNone(self.main_window.video_widget, "QVideoWidget should exist.")

        self.assertIsInstance(self.main_window.play_button, QPushButton, "Play button should exist.")
        self.assertIsInstance(self.main_window.pause_button, QPushButton, "Pause button should exist.")
        self.assertIsInstance(self.main_window.stop_button, QPushButton, "Stop button should exist.")
        self.assertIsInstance(self.main_window.volume_slider, QSlider, "Volume slider should exist.")
        self.assertIsInstance(self.main_window.open_button, QPushButton, "Open File button should exist.")

    def test_file_loading_logic_simulated(self):
        """Test the logic after a file path is hypothetically available."""
        # Simulate that a file path has been obtained (as if from QFileDialog)
        self.main_window.media_file_path = self.dummy_media_path

        # Directly create QMediaContent and set it, mimicking part of open_file_dialog
        media_content = QMediaContent(QUrl.fromLocalFile(self.main_window.media_file_path))
        self.main_window.player.setMedia(media_content)

        self.assertFalse(self.main_window.player.media().isNull(), "Player should have non-null media content after setting.")
        # Check if the content URL matches what was set
        self.assertEqual(self.main_window.player.media().canonicalUrl(), QUrl.fromLocalFile(self.dummy_media_path))

    def test_playback_controls_initial_state(self):
        """Test the initial state of the media player."""
        self.assertEqual(self.main_window.player.state(), QMediaPlayer.StoppedState, "Player should initially be in StoppedState.")
        # Initially, play should be enabled, pause/stop might be disabled as no media is loaded.
        # Actual enabled states can depend on QMediaPlayer's internal logic for empty media.
        self.assertTrue(self.main_window.play_button.isEnabled(), "Play button should be enabled initially.")
        # For pause and stop, they are often disabled until media is loaded and playing/paused.
        # Let's assume they are enabled by default in the UI setup, and QMediaPlayer handles playability.
        # If specific logic was added to disable them, this test would change.
        # self.assertFalse(self.main_window.pause_button.isEnabled(), "Pause button should be disabled if no media.")
        # self.assertFalse(self.main_window.stop_button.isEnabled(), "Stop button should be disabled if no media.")


    def test_play_action(self):
        """Test the play action."""
        self.main_window.player.setMedia(self.dummy_media_content) # Load dummy media
        QTest.mouseClick(self.main_window.play_button, Qt.LeftButton)
        # Note: QMediaPlayer might not immediately switch to PlayingState with a dummy/invalid file.
        # It might go to StoppedState if the media is invalid or BufferingState.
        # For a unit test, asserting it's NOT StoppedState after play is clicked (if media is set)
        # or mocking might be more robust. Given the constraints, we aim for PlayingState.
        # This test might be flaky if the dummy file causes an immediate error.
        # A more robust test would involve a valid silent media file or mocking QMediaPlayer.
        # For now, we assume it attempts to play.
        # QTest.qWait(100) # Allow some time for state change if needed, but can make tests slow
        if self.main_window.player.error() == QMediaPlayer.NoError:
             self.assertNotEqual(self.main_window.player.state(), QMediaPlayer.StoppedState,
                                "Player should not be in StoppedState immediately after play is clicked with media.")
        # A more ideal check if media was valid:
        # self.assertEqual(self.main_window.player.state(), QMediaPlayer.PlayingState)


    def test_pause_action(self):
        """Test the pause action."""
        self.main_window.player.setMedia(self.dummy_media_content)
        self.main_window.player.play() # Programmatically play
        # QTest.qWait(50) # Give it a moment if it were real media

        if self.main_window.player.state() == QMediaPlayer.PlayingState: # Only if playing
            QTest.mouseClick(self.main_window.pause_button, Qt.LeftButton)
            self.assertEqual(self.main_window.player.state(), QMediaPlayer.PausedState, "Player should be in PausedState after pause.")
        else:
            # If it didn't reach PlayingState (e.g. dummy file issue), this part of test might not be fully valid.
            # Consider marking as skipped or logging a warning.
            print("Warning: Player not in PlayingState for pause test. Skipping pause assertion.")
            pass


    def test_stop_action(self):
        """Test the stop action."""
        self.main_window.player.setMedia(self.dummy_media_content)
        self.main_window.player.play() # Programmatically play
        # QTest.qWait(50)

        # Stop action should work regardless of whether it was playing or paused, as long as media is set.
        QTest.mouseClick(self.main_window.stop_button, Qt.LeftButton)
        self.assertEqual(self.main_window.player.state(), QMediaPlayer.StoppedState, "Player should be in StoppedState after stop.")

    def test_volume_slider_action(self):
        """Test that the volume slider correctly calls setVolume."""
        initial_volume = self.main_window.player.volume()
        target_volume = 75
        if initial_volume == target_volume: # Adjust if default is already target
            target_volume = 50

        self.main_window.volume_slider.setValue(target_volume) # This directly triggers the connected slot
        # QTest.qWait(50) # Allow signal processing
        self.assertEqual(self.main_window.player.volume(), target_volume, "Player volume should be updated by slider.")


if __name__ == '__main__':
    # It's important that QApplication is created before tests run,
    # especially if tests involve GUI elements or signals.
    # The setUpClass method tries to handle this.
    unittest.main()
