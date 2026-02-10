# widgets/log_viewer_dialog.py
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTextBrowser,
    QSlider,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# We'll import get_log_filename from utils.logging
from utils.logging import get_log_filename


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Today's Log")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left: Text area
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 11))
        self.log_display.setStyleSheet("""
            QTextBrowser {
                background: #222;
                color: #e0e0e0;
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;
            }
        """)
        text_layout.addWidget(self.log_display)

        # Right: Slider + Refresh button
        slider_container = QWidget()
        slider_container.setFixedWidth(30)
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(0)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setInvertedAppearance(True)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #3a3a3a;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }
            QSlider::handle:vertical {
                background: #6b5a47;
                border: 1px solid #8a7a67;
                height: 18px;
                width: 18px;
                margin: -6px -6px -6px -6px;
                border-radius: 9px;
            }
            QSlider::handle:vertical:hover {
                background: #8a7a67;
            }
        """)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(30)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 6px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        refresh_btn.clicked.connect(self.load_log_content)
        slider_layout.addWidget(refresh_btn)

        main_layout.addWidget(text_container, stretch=1)
        main_layout.addWidget(slider_container)

        self.load_log_content()

        # Connect scroll sync
        self.log_display.verticalScrollBar().valueChanged.connect(self.update_slider_from_text)
        self.log_display.document().contentsChanged.connect(self.update_slider_range)

    def load_log_content(self):
        log_file = get_log_filename()
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_text = f.read()
            self.log_display.clear()
            self.log_display.setPlainText(log_text)
            # Auto-scroll to bottom
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )
        else:
            self.log_display.clear()
            self.log_display.setPlainText(
                "No activity logged today yet.\nCome back after uploading something! ☕"
            )

        self.update_slider_range()
        # Small delay to let Qt settle layout/scrollbar
        QTimer.singleShot(50, self.update_slider_range)

    def update_slider_range(self):
        max_scroll = self.log_display.verticalScrollBar().maximum()
        self.slider.setRange(0, max_scroll if max_scroll > 0 else 100)
        # Default to bottom on load/refresh
        self.slider.setValue(self.slider.maximum())

    def on_slider_changed(self, value):
        self.log_display.verticalScrollBar().setValue(value)

    def update_slider_from_text(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)