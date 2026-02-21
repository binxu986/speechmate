"""
SpeechMate System Tray Icon
"""
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont


class TrayIcon(QSystemTrayIcon, QObject):
    """System tray icon for SpeechMate"""

    quit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        QObject.__init__(self)

        self._create_icon()
        self._create_menu()

    def _create_icon(self):
        """Create tray icon"""
        # Create a simple icon with a microphone symbol
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw circle background
        painter.setBrush(QColor(79, 70, 229))  # Indigo color
        painter.setPen(QColor(79, 70, 229))
        painter.drawEllipse(4, 4, 56, 56)

        # Draw microphone icon
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))

        # Mic body
        painter.drawRoundedRect(24, 14, 16, 26, 8, 8)

        # Mic base
        painter.drawRoundedRect(20, 36, 24, 4, 2, 2)

        # Mic stand
        painter.drawRect(31, 40, 2, 10)

        # Mic arc
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawArc(20, 20, 24, 30, 0, -180 * 16)

        painter.end()

        self.setIcon(QIcon(pixmap))
        self.setToolTip("SpeechMate - 语音识别助手")

    def _create_menu(self):
        """Create context menu"""
        menu = QMenu()

        # Show window action
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        # Quick actions
        transcribe_action = QAction("语音识别", self)
        transcribe_action.triggered.connect(self._trigger_transcribe)
        menu.addAction(transcribe_action)

        translate_zh_action = QAction("中译英", self)
        translate_zh_action.triggered.connect(self._trigger_translate_zh)
        menu.addAction(translate_zh_action)

        translate_en_action = QAction("英译中", self)
        translate_en_action.triggered.connect(self._trigger_translate_en)
        menu.addAction(translate_en_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_clicked)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _show_window(self):
        """Show main window"""
        if self.parent():
            self.parent().show()
            self.parent().activateWindow()

    def _trigger_transcribe(self):
        """Trigger transcribe action"""
        from app.hotkey import HotkeyAction, hotkey_listener
        callback = hotkey_listener._callbacks.get(HotkeyAction.TRANSCRIBE)
        if callback:
            callback()

    def _trigger_translate_zh(self):
        """Trigger translate zh->en action"""
        from app.hotkey import HotkeyAction, hotkey_listener
        callback = hotkey_listener._callbacks.get(HotkeyAction.TRANSLATE_ZH_TO_EN)
        if callback:
            callback()

    def _trigger_translate_en(self):
        """Trigger translate en->zh action"""
        from app.hotkey import HotkeyAction, hotkey_listener
        callback = hotkey_listener._callbacks.get(HotkeyAction.TRANSLATE_EN_TO_ZH)
        if callback:
            callback()

    def set_recording_state(self, is_recording: bool):
        """Update icon to show recording state"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if is_recording:
            # Red background for recording
            painter.setBrush(QColor(239, 68, 68))  # Red color
            painter.setPen(QColor(239, 68, 68))
        else:
            # Normal indigo background
            painter.setBrush(QColor(79, 70, 229))
            painter.setPen(QColor(79, 70, 229))

        painter.drawEllipse(4, 4, 56, 56)

        # Draw microphone icon
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))

        # Mic body
        painter.drawRoundedRect(24, 14, 16, 26, 8, 8)

        painter.end()

        self.setIcon(QIcon(pixmap))


# Import QPen for arc drawing
from PyQt5.QtGui import QPen
