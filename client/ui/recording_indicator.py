"""
SpeechMate Recording Indicator
A floating window that shows recording status
"""
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush


class RecordingIndicator(QWidget):
    """Floating recording indicator widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._opacity = 1.0
        self._pulse_direction = -1

        self._init_ui()

        # Pulse animation timer
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._pulse)

    def _init_ui(self):
        """Initialize UI"""
        # Window flags for floating window
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Size
        self.setFixedSize(120, 120)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        # Position in bottom-right corner
        self._update_position()

    def _update_position(self):
        """Update position to bottom-right corner"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.width() - self.width() - 30
            y = geometry.height() - self.height() - 80
            self.move(x, y)

    def show_recording(self):
        """Show indicator in recording state"""
        self._opacity = 1.0
        self.show()
        self._pulse_timer.start(30)

    def hide_indicator(self):
        """Hide indicator"""
        self._pulse_timer.stop()
        self.hide()

    def hide(self):
        """Override hide to stop animation"""
        self._pulse_timer.stop()
        super().hide()

    def _pulse(self):
        """Pulse animation"""
        self._opacity += self._pulse_direction * 0.02

        if self._opacity <= 0.5:
            self._pulse_direction = 1
        elif self._opacity >= 1.0:
            self._pulse_direction = -1

        self.update()

    def paintEvent(self, event):
        """Paint the indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background circle
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 45

        # Outer circle with glow
        glow_color = QColor(239, 68, 68, int(50 * self._opacity))
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius - 10, center_y - radius - 10,
                           (radius + 10) * 2, (radius + 10) * 2)

        # Main circle
        main_color = QColor(239, 68, 68, int(255 * self._opacity))
        painter.setBrush(QBrush(main_color))
        painter.drawEllipse(center_x - radius, center_y - radius,
                           radius * 2, radius * 2)

        # Draw microphone icon
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(QBrush(QColor(255, 255, 255)))

        # Mic body (rounded rectangle)
        mic_width = 14
        mic_height = 24
        mic_x = center_x - mic_width // 2
        mic_y = center_y - mic_height // 2 - 4

        painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, 7, 7)

        # Mic stand
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(center_x - 1, center_y + 8, 2, 10)

        # Mic arc
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawArc(center_x - 15, center_y - 8, 30, 30, 0, -180 * 16)

        # Recording text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, self.height() - 15, self.width(), 15,
                        Qt.AlignCenter, "录音中...")

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)
