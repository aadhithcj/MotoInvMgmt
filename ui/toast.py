from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QPoint, QEasingCurve
from PyQt6.QtGui import QColor, QPalette

class ToastNotification(QWidget):
    """
    A non-blocking overlay notification (Toast) that slides in from the bottom 
    and fades out automatically.
    """
    _instance = None
    
    @classmethod
    def show_toast(cls, parent, message, type="success", duration=3000):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            
        cls._instance = cls(parent, message, type, duration)
        cls._instance.show()

    def __init__(self, parent, message, type="success", duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.setup_ui(message, type)
        self.duration = duration
        
        # Initial position (bottom right)
        self.adjustSize()
        self.update_position()
        
        # Animations
        self.start_animations()

    def setup_ui(self, message, type):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl = QLabel(message)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Styling based on type
        is_dark = self.parent().palette().window().color().lightness() < 128
        
        if type == "success":
            bg_color = "#064E3B" if is_dark else "#DCFCE7"
            text_color = "#A7F3D0" if is_dark else "#166534"
            border_color = "#047857" if is_dark else "#22C55E"
        elif type == "error":
            bg_color = "#7F1D1D" if is_dark else "#FEE2E2"
            text_color = "#FECACA" if is_dark else "#991B1B"
            border_color = "#B91C1C" if is_dark else "#EF4444"
        else: # info
            bg_color = "#1E3A8A" if is_dark else "#DBEAFE"
            text_color = "#BFDBFE" if is_dark else "#1E40AF"
            border_color = "#1D4ED8" if is_dark else "#3B82F6"
            
        self.lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        layout.addWidget(self.lbl)

    def update_position(self):
        parent_rect = self.parent().geometry()
        x = parent_rect.x() + parent_rect.width() - self.width() - 30
        y = parent_rect.y() + parent_rect.height() - self.height() - 30
        self.move(x, y)

    def start_animations(self):
        # Slide in from bottom
        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(400)
        start_pos = QPoint(self.x(), self.y() + 50)
        end_pos = QPoint(self.x(), self.y())
        self.anim_pos.setStartValue(start_pos)
        self.anim_pos.setEndValue(end_pos)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # Fade in
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        
        self.anim_pos.start()
        self.anim_opacity.start()
        
        # Schedule fade out
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(self.duration)

    def fade_out(self):
        self.anim_opacity.setStartValue(1.0)
        self.anim_opacity.setEndValue(0.0)
        self.anim_opacity.setDuration(400)
        self.anim_opacity.finished.connect(self.close)
        self.anim_opacity.start()
