# dialogs/settings_dialog.py
import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

from utils.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings ⚙")
        self.setFixedSize(520, 260)           # wider but shorter
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header
        header = QLabel("Preferences")
        header.setFont(QFont("Lato", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #8a7a67;")
        main_layout.addWidget(header)

        main_layout.addSpacing(10)

        # ── Horizontal two-column container ─────────────────────────────
        columns = QHBoxLayout()
        columns.setSpacing(24)

        # Left: App Icon
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        app_title = QLabel("App Window Icon")
        app_title.setFont(QFont("Lato", 14, QFont.Bold))
        app_title.setAlignment(Qt.AlignCenter)
        left_col.addWidget(app_title)

        self.app_status = QLabel("No custom icon set")
        self.app_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        self.app_status.setAlignment(Qt.AlignCenter)
        self.app_status.setWordWrap(True)
        left_col.addWidget(self.app_status)

        self.app_preview = QLabel()
        self.app_preview.setFixedSize(32, 32)
        self.app_preview.setAlignment(Qt.AlignCenter)
        left_col.addWidget(self.app_preview, alignment=Qt.AlignCenter)

        app_btn = QPushButton("Choose Icon")
        app_btn.setFixedHeight(36)
        app_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        app_btn.clicked.connect(self.choose_app_icon)
        left_col.addWidget(app_btn)

        app_reset = QPushButton("Reset")
        app_reset.setFixedHeight(28)
        app_reset.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #4a3a2f;
                border-radius: 6px;
                color: #a08a7a;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333;
                color: #e0e0e0;
            }
        """)
        app_reset.clicked.connect(lambda: self.reset_icon("icon_path", self.app_status, self.app_preview))
        left_col.addWidget(app_reset)

        left_col.addStretch()
        columns.addLayout(left_col)

        # Right: Bullet Icon
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        bullet_title = QLabel("Feature List Bullet")
        bullet_title.setFont(QFont("Lato", 14, QFont.Bold))
        bullet_title.setAlignment(Qt.AlignCenter)
        right_col.addWidget(bullet_title)

        self.bullet_status = QLabel("Using default")
        self.bullet_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        self.bullet_status.setAlignment(Qt.AlignCenter)
        self.bullet_status.setWordWrap(True)
        right_col.addWidget(self.bullet_status)

        self.bullet_preview = QLabel()
        self.bullet_preview.setFixedSize(32, 32)
        self.bullet_preview.setAlignment(Qt.AlignCenter)
        right_col.addWidget(self.bullet_preview, alignment=Qt.AlignCenter)

        bullet_btn = QPushButton("Choose Icon")
        bullet_btn.setFixedHeight(36)
        bullet_btn.setStyleSheet(app_btn.styleSheet())
        bullet_btn.clicked.connect(self.choose_bullet_icon)
        right_col.addWidget(bullet_btn)

        bullet_reset = QPushButton("Reset")
        bullet_reset.setFixedHeight(28)
        bullet_reset.setStyleSheet(app_reset.styleSheet())
        bullet_reset.clicked.connect(lambda: self.reset_icon("bullet_icon_path", self.bullet_status, self.bullet_preview))
        right_col.addWidget(bullet_reset)

        right_col.addStretch()
        columns.addLayout(right_col)

        main_layout.addLayout(columns)

        main_layout.addStretch()

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(38)
        close_btn.setStyleSheet(app_btn.styleSheet())
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)

        main_layout.addLayout(footer)

        self._refresh_statuses()

    def _refresh_statuses(self):
        # App icon
        app_path = Settings.get("icon_path")
        if app_path and os.path.exists(app_path):
            self.app_status.setText(os.path.basename(app_path))
            pix = QPixmap(app_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.app_preview.setPixmap(pix)
        else:
            self.app_status.setText("No custom icon")
            self.app_preview.clear()

        # Bullet icon
        bullet_path = Settings.get("bullet_icon_path")
        if bullet_path and os.path.exists(bullet_path):
            self.bullet_status.setText(os.path.basename(bullet_path))
            pix = QPixmap(bullet_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.bullet_preview.setPixmap(pix)
        else:
            self.bullet_status.setText("Default")
            self.bullet_preview.clear()

    def choose_app_icon(self):
        start_dir = Settings.get_directory("last_dir_icon")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select App Icon", start_dir, "Icons (*.ico *.png *.jpg *.jpeg)"
        )
        if path and os.path.exists(path):
            try:
                self.parent().setWindowIcon(QIcon(path))
                Settings.set("icon_path", path)
                Settings.set_directory("last_dir_icon", path)
                self._refresh_statuses()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not set app icon:\n{str(e)}")

    def choose_bullet_icon(self):
        start_dir = Settings.get_directory("last_dir_bullet") or Settings.get_directory("last_dir_icon") or ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Bullet Icon", start_dir, "Images (*.png *.ico *.jpg *.jpeg)"
        )
        if path and os.path.exists(path):
            try:
                pix = QPixmap(path)
                if pix.isNull():
                    raise ValueError("Invalid image")
                Settings.set("bullet_icon_path", path)
                Settings.set_directory("last_dir_bullet", path)
                self._refresh_statuses()
                QMessageBox.information(self, "Updated", "Bullet icon changed.\n(Re-open feature list to see it.)")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not set bullet icon:\n{str(e)}")

    def reset_icon(self, key: str, status_label: QLabel, preview: QLabel):
        Settings.set(key, None)
        status_label.setText("Default" if key == "bullet_icon_path" else "No custom icon")
        preview.clear()