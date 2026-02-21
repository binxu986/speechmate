"""
SpeechMate Client Main Window
"""
import sys
import threading
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QCheckBox, QMessageBox, QSystemTrayIcon, QMenu, QAction,
    QApplication, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from loguru import logger

from app.config import config, save_config, ClientConfig, HotkeyConfig
from app.api_client import api_client
from app.recorder import recorder
from app.text_input import output_text
from app.hotkey import hotkey_listener, HotkeyAction
from ui.tray_icon import TrayIcon
from ui.recording_indicator import RecordingIndicator


class MainWindow(QMainWindow):
    """Main application window"""

    # Signal for thread-safe UI updates
    status_signal = pyqtSignal(str)
    processing_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SpeechMate")
        self.setMinimumSize(450, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        # Initialize UI components
        self._init_ui()
        self._init_tray()
        self._init_hotkeys()
        self._init_recording_indicator()

        # Connect signals
        self.status_signal.connect(self._update_status)
        self.processing_signal.connect(self._set_processing)

        # Load config to UI
        self._load_config_to_ui()

        # Initialize API client
        api_client.set_base_url(config.base_url)
        api_client.set_api_key(config.api_key)

        # Check server connection
        QTimer.singleShot(500, self._check_server_connection)

    def _init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("SpeechMate")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Server connection group
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout(server_group)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("http://localhost:8000")
        server_layout.addRow("Base URL:", self.base_url_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        server_layout.addRow("API Key:", self.api_key_input)

        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self._test_connection)
        server_layout.addRow("", self.test_btn)

        layout.addWidget(server_group)

        # Hotkey settings group
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QFormLayout(hotkey_group)

        self.transcribe_key_input = QLineEdit()
        self.transcribe_key_input.setPlaceholderText("alt")
        hotkey_layout.addRow("语音识别:", self.transcribe_key_input)

        self.translate_zh_en_input = QLineEdit()
        self.translate_zh_en_input.setPlaceholderText("shift")
        hotkey_layout.addRow("中译英:", self.translate_zh_en_input)

        self.translate_en_zh_input = QLineEdit()
        self.translate_en_zh_input.setPlaceholderText("shift+a")
        hotkey_layout.addRow("英译中:", self.translate_en_zh_input)

        layout.addWidget(hotkey_group)

        # Options group
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout(options_group)

        self.minimize_cb = QCheckBox("关闭时最小化到系统托盘")
        options_layout.addWidget(self.minimize_cb)

        self.show_indicator_cb = QCheckBox("显示录音状态指示器")
        self.show_indicator_cb.setChecked(True)
        options_layout.addWidget(self.show_indicator_cb)

        layout.addWidget(options_group)

        # Status label
        self.status_label = QLabel("状态: 就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Save button
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self._save_settings)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def _init_tray(self):
        """Initialize system tray icon"""
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

        # Handle tray icon events
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.quit_clicked.connect(self._quit_app)

    def _init_hotkeys(self):
        """Initialize hotkey listener"""
        hotkey_listener.set_callback(HotkeyAction.TRANSCRIBE, self._on_transcribe)
        hotkey_listener.set_callback(HotkeyAction.TRANSLATE_ZH_TO_EN, self._on_translate_zh_to_en)
        hotkey_listener.set_callback(HotkeyAction.TRANSLATE_EN_TO_ZH, self._on_translate_en_to_zh)
        hotkey_listener.start()

    def _init_recording_indicator(self):
        """Initialize recording indicator"""
        self.recording_indicator = RecordingIndicator()

        # Update indicator visibility based on config
        self.show_indicator_cb.stateChanged.connect(
            lambda state: self.recording_indicator.setVisible(state == Qt.Checked)
        )

    def _load_config_to_ui(self):
        """Load configuration to UI"""
        self.base_url_input.setText(config.base_url)
        self.api_key_input.setText(config.api_key)
        self.transcribe_key_input.setText(config.hotkeys.transcribe)
        self.translate_zh_en_input.setText(config.hotkeys.translate_zh_to_en)
        self.translate_en_zh_input.setText(config.hotkeys.translate_en_to_zh)
        self.minimize_cb.setChecked(config.minimize_to_tray)
        self.show_indicator_cb.setChecked(config.show_recording_indicator)

    def _save_settings(self):
        """Save settings from UI"""
        config.base_url = self.base_url_input.text().strip()
        config.api_key = self.api_key_input.text().strip()
        config.hotkeys.transcribe = self.transcribe_key_input.text().strip() or "alt"
        config.hotkeys.translate_zh_to_en = self.translate_zh_en_input.text().strip() or "shift"
        config.hotkeys.translate_en_to_zh = self.translate_en_zh_input.text().strip() or "shift+a"
        config.minimize_to_tray = self.minimize_cb.isChecked()
        config.show_recording_indicator = self.show_indicator_cb.isChecked()

        save_config(config)

        # Update API client
        api_client.set_base_url(config.base_url)
        api_client.set_api_key(config.api_key)

        self._update_status("设置已保存")

    def _check_server_connection(self):
        """Check server connection on startup"""
        if api_client.health_check():
            self._update_status("状态: 已连接到服务器")
        else:
            self._update_status("状态: 无法连接到服务器")

    def _test_connection(self):
        """Test server connection"""
        self._update_status("正在测试连接...")

        # Update API client with current values
        api_client.set_base_url(self.base_url_input.text().strip())
        api_client.set_api_key(self.api_key_input.text().strip())

        if api_client.health_check():
            self._update_status("连接成功!")
            QMessageBox.information(self, "成功", "服务器连接成功!")
        else:
            self._update_status("连接失败")
            QMessageBox.warning(self, "失败", "无法连接到服务器，请检查 URL 和 API Key")

    def _update_status(self, text: str):
        """Update status label"""
        self.status_label.setText(f"状态: {text}")
        logger.info(text)

    def _set_processing(self, is_processing: bool):
        """Set processing state"""
        if is_processing:
            self.setEnabled(False)
            hotkey_listener.pause()
        else:
            self.setEnabled(True)
            hotkey_listener.resume()

    def _on_transcribe(self):
        """Handle transcribe hotkey"""
        logger.info("Transcribe hotkey triggered")
        self._start_recording("transcribe")

    def _on_translate_zh_to_en(self):
        """Handle translate zh->en hotkey"""
        logger.info("Translate zh->en hotkey triggered")
        self._start_recording("translate_zh_en")

    def _on_translate_en_to_zh(self):
        """Handle translate en->zh hotkey"""
        logger.info("Translate en->zh hotkey triggered")
        self._start_recording("translate_en_zh")

    def _start_recording(self, mode: str):
        """Start recording audio"""
        if recorder.is_recording:
            logger.warning("Already recording")
            return

        self.recording_mode = mode
        self.status_signal.emit("正在录音...")

        # Show recording indicator
        if config.show_recording_indicator:
            self.recording_indicator.show_recording()

        # Start recording
        recorder.start_recording()

        # Wait for key release (handled by recorder callback)
        # For now, we'll use a timer-based approach
        self._recording_timer = QTimer()
        self._recording_timer.timeout.connect(self._check_recording_done)
        self._recording_timer.start(100)

    def _check_recording_done(self):
        """Check if recording should stop"""
        # Check if hotkey is still pressed
        from pynput import keyboard

        # Get current hotkey
        if self.recording_mode == "transcribe":
            key_str = config.hotkeys.transcribe
        elif self.recording_mode == "translate_zh_en":
            key_str = config.hotkeys.translate_zh_to_en
        else:
            key_str = config.hotkeys.translate_en_to_zh

        # Check if modifier key is still pressed
        still_pressed = False

        if "shift" in key_str.lower():
            still_pressed = any(k.is_pressed for k in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r])
        if "alt" in key_str.lower():
            still_pressed = still_pressed or any(k.is_pressed for k in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r])
        if "ctrl" in key_str.lower():
            still_pressed = still_pressed or any(k.is_pressed for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r])

        if not still_pressed:
            self._recording_timer.stop()
            self._stop_recording()

    def _stop_recording(self):
        """Stop recording and process audio"""
        self.recording_indicator.hide()
        self.status_signal.emit("正在处理...")

        # Stop recording
        audio_path = recorder.stop_recording()

        if not audio_path:
            self.status_signal.emit("录音太短或失败")
            return

        # Process in background thread
        thread = threading.Thread(
            target=self._process_audio,
            args=(audio_path, self.recording_mode),
            daemon=True
        )
        thread.start()

    def _process_audio(self, audio_path: str, mode: str):
        """Process recorded audio"""
        self.processing_signal.emit(True)

        try:
            if mode == "transcribe":
                success, text, error = api_client.transcribe(audio_path)
                if success and text:
                    output_text(text)
                    self.status_signal.emit(f"识别完成: {text[:30]}...")
                else:
                    self.status_signal.emit(f"识别失败: {error}")

            elif mode == "translate_zh_en":
                success, original, translated, error = api_client.translate(
                    audio_path, "zh", "en"
                )
                if success and translated:
                    output_text(translated)
                    self.status_signal.emit(f"翻译完成: {translated[:30]}...")
                else:
                    self.status_signal.emit(f"翻译失败: {error}")

            elif mode == "translate_en_zh":
                success, original, translated, error = api_client.translate(
                    audio_path, "en", "zh"
                )
                if success and translated:
                    output_text(translated)
                    self.status_signal.emit(f"翻译完成: {translated[:30]}...")
                else:
                    self.status_signal.emit(f"翻译失败: {error}")

        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.status_signal.emit(f"处理失败: {e}")

        finally:
            self.processing_signal.emit(False)

            # Clean up audio file
            try:
                import os
                os.unlink(audio_path)
            except:
                pass

    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def closeEvent(self, event):
        """Handle window close event"""
        if config.minimize_to_tray:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "SpeechMate",
                "程序已最小化到系统托盘",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self._quit_app()

    def _quit_app(self):
        """Quit application"""
        hotkey_listener.stop()
        self.tray_icon.hide()
        QApplication.quit()
