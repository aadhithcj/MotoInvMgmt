from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class LoadingOverlay(QDialog):
    def __init__(self, parent=None, message="Scanning bill with AI..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(320, 140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        
        self.label = QLabel(message)
        self.label.setStyleSheet("""
            QLabel {
                color: #F8FAFC;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.sub_label = QLabel("Please wait, this may take a few moments.")
        self.sub_label.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 13px;
                background: transparent;
                border: none;
            }
        """)
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        frame_layout.addStretch()
        frame_layout.addWidget(self.label)
        frame_layout.addWidget(self.sub_label)
        frame_layout.addStretch()
        
        layout.addWidget(self.frame)
