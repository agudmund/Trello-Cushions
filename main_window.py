# main_window.py
import sys
import os
import time
import webbrowser
from datetime import datetime
import requests

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QToolButton,
    QStyle,
)
from PySide6.QtCore import Qt, QSize 
from PySide6.QtGui import QFont, QColor, QIcon

from utils.logging import log_message
from utils.trello_api import (
    get_credentials,
    create_board,
    create_list,
    create_card,
)
from utils.settings import Settings
from widgets.drop_area import CozyDropArea
from dialogs.settings_dialog import SettingsDialog
from widgets.feature_list_dialog import FeatureListDialog
from widgets.log_viewer_dialog import LogViewerDialog
from widgets.about_dialog import AboutDialog   # ← new import


class TrelloCushionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trello Cushions 🌱")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        # Load saved custom icon at startup (if exists)
        icon_path = Settings.get("icon_path")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()

        log_btn = QToolButton(self)
        log_btn.setText("📜")
        log_btn.setFont(QFont("Segoe UI Emoji", 18))
        log_btn.setStyleSheet("""
            QToolButton { background: transparent; color: #8a7a67; border: none; }
            QToolButton:hover { color: #fff; }
        """)
        log_btn.setFixedSize(40, 40)
        log_btn.clicked.connect(self.show_log)
        top_layout.addWidget(log_btn)

        features_btn = QToolButton(self)
        features_btn.setText("📋")
        features_btn.setFont(QFont("Segoe UI Emoji", 18))
        features_btn.setStyleSheet("""
            QToolButton { background: transparent; color: #8a7a67; border: none; }
            QToolButton:hover { color: #fff; }
        """)
        features_btn.setFixedSize(40, 40)
        features_btn.clicked.connect(self.show_feature_list)
        top_layout.addWidget(features_btn)

        settings_btn = QToolButton(self)
        settings_btn.setText("⚙")
        settings_btn.setFont(QFont("Segoe UI Emoji", 18))
        settings_btn.setStyleSheet("""
            QToolButton { background: transparent; color: #8a7a67; border: none; }
            QToolButton:hover { color: #fff; }
        """)
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(settings_btn)

        # New: About button
        about_btn = QToolButton(self)
        about_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        about_btn.setIconSize(QSize(24, 24))
        about_btn.setStyleSheet("""
            QToolButton { background: transparent; border: none; }
            QToolButton:hover { background: rgba(255,255,255,20); border-radius: 4px; }
        """)
        about_btn.setFixedSize(40, 40)
        about_btn.clicked.connect(self.show_about)
        top_layout.addWidget(about_btn)

        layout.addWidget(top_bar)

        title = QLabel("Upload to Trello Cushions")
        title.setFont(QFont("Lato", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.drop_area = CozyDropArea()
        layout.addWidget(self.drop_area)

        browse_btn = QPushButton("Browse File")
        browse_btn.setFixedHeight(40)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)

        self.status_label = QLabel("Drag or browse a .md/.txt file to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8a7a67; font-size: 13px;")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        central.setGraphicsEffect(shadow)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_feature_list(self):
        dialog = FeatureListDialog(self)
        dialog.exec()

    def show_log(self):
        dialog = LogViewerDialog(self)
        dialog.exec()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def browse_file(self):
        start_dir = Settings.get_directory("last_dir_upload")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .md/.txt File", start_dir, "Text/Markdown Files (*.txt *.md)"
        )
        if path:
            Settings.set_directory("last_dir_upload", path)
            self.process_file(path)

    def process_file(self, path):
        self.status_label.setText(f"Processing {os.path.basename(path)}...")
        self.progress.setVisible(True)
        self.progress.setValue(0)

        try:
            log_message(f"Starting upload of {path}")
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            total = len(paragraphs)
            if total == 0:
                log_message(f"No paragraphs found in {path}")
                self.status_label.setText("File is empty or has no paragraphs.")
                self.progress.setVisible(False)
                return

            log_message(f"Found {total} paragraphs")
            self.progress.setRange(0, total)
            api_key, token = get_credentials()
            if not api_key or not token:
                log_message("Keys not found")
                self.status_label.setText("Keys not found. Set TRELLO_KEY and TRELLO_TOKEN.")
                self.progress.setVisible(False)
                return

            board_id, board_url = create_board(api_key, token)
            todo_id = create_list(api_key, token, board_id, "To Review 🌅")

            cards_added = 0
            for i, para in enumerate(paragraphs, 1):
                card_name = f"Note {i}"
                desc = para[:4000] + "…" if len(para) > 4000 else para
                if create_card(api_key, token, todo_id, card_name, desc):
                    cards_added += 1
                self.progress.setValue(i)
                QApplication.processEvents()
                time.sleep(0.6)

            self.progress.setVisible(False)
            summary = f"Done! {cards_added} cards added."
            self.status_label.setText(summary)
            log_message(summary)
            reply = QMessageBox.question(
                self, "Success", f"Board created with {cards_added} cards.\nOpen now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                webbrowser.open(board_url)

        except Exception as e:
            error_msg = f"Error during upload: {str(e)}"
            log_message(error_msg)
            self.status_label.setText(f"Error: {str(e)}")
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", str(e))