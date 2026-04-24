import sys
import json
import os
import shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QMessageBox, QPushButton, 
                             QFileDialog, QInputDialog, QLabel)
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtCore import QSize, Qt

class AestheticReactionBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Reaction Clipboard")
        self.resize(700, 600) # Replicated a similar aspect ratio and size
        self.emoji_data = {}

        # --- File System Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_path = os.path.join(self.base_dir, "emojis.json")
        self.images_dir = os.path.join(self.base_dir, "images")

        # Ensure directory structure exists on first run
        os.makedirs(self.images_dir, exist_ok=True)
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump({}, f)

        # --- Replicated Aesthetic QSS (Qt Style Sheet) ---
        # Sampling colors from user design:
        # Background: #16161a
        # Inputs/Tiles: #222226
        # Borders: #313244
        # Accent Text: #55555e
        self.setStyleSheet("""
            QWidget {
                background-color: #16161a;
                color: #cdd6f4;
                font-family: 'Inter', 'Segoe UI', Helvetica, Arial, sans-serif;
            }
            QLabel#sectionHeader {
                color: #55555e;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                margin-top: 5px;
                margin-bottom: 2px;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #313244;
                border-radius: 8px;
                background-color: #222226;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                padding: 12px 18px;
                background-color: transparent;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
                font-weight: normal;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #222226;
                border: 1px solid #44475a;
            }
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            /* The entire QListWidgetItem container */
            QListWidget::item {
                border: 1px solid #313244;
                background-color: #222226;
                border-radius: 16px; # Replicated large rounded corners
                margin: 5px;
                padding: 8px;
            }
            QListWidget::item:hover {
                border: 1px solid #44475a;
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #313244;
                border: 1px solid #89b4fa;
            }
        """)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # --- Replicated Top Bar Layout ---
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(10)
        
        # Replicated magnifying glass placeholder in the search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search reactions...")
        self.search_bar.textChanged.connect(self.filter_emojis)
        top_bar_layout.addWidget(self.search_bar, 1) # Set stretch so search bar is primary

        self.add_btn = QPushButton("+ Add Reaction")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_new_emoji)
        top_bar_layout.addWidget(self.add_btn)

        main_layout.addLayout(top_bar_layout)

        # --- Section Header ---
        section_header = QLabel("All Reactions")
        section_header.setObjectName("sectionHeader")
        main_layout.addWidget(section_header)

        # --- Replicated Image Grid ---
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        # Using larger tiles as in the replicated design, with icon fitting inside
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(10) # Minimal internal spacing for a cleaner grid
        self.list_widget.itemClicked.connect(self.copy_to_clipboard)
        main_layout.addWidget(self.list_widget)

        # --- Load Initial Data ---
        self.load_data()

    def load_data(self):
        """Loads data from the JSON file."""
        try:
            with open(self.json_path, "r") as f:
                self.emoji_data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load JSON: {e}")
            self.emoji_data = {}
            
        self.populate_grid()

    def save_data(self):
        """Saves current data to the JSON file."""
        try:
            with open(self.json_path, "w") as f:
                json.dump(self.emoji_data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def populate_grid(self, search_text=""):
        """Fills the grid with images that match the search text."""
        self.list_widget.clear()
        search_text = search_text.lower()

        for name, rel_path in self.emoji_data.items():
            if search_text in name.lower() or search_text == "":
                # Convert the relative path from JSON to an absolute path for the OS
                # and use os.path.normpath to ensure it works on Windows and Linux
                abs_path = os.path.join(self.base_dir, os.path.normpath(rel_path))
                
                if os.path.exists(abs_path):
                    item = QListWidgetItem()
                    item.setIcon(QIcon(abs_path))
                    item.setData(Qt.ItemDataRole.UserRole, abs_path)
                    item.setToolTip(name.title()) # Capitalize tooltip for aesthetics
                    self.list_widget.addItem(item)
                else:
                    # In a proper app, we'd log this, not make a popup during load
                    print(f"Warning: Image missing at path {abs_path}")

    def filter_emojis(self, text):
        self.populate_grid(text)

    def add_new_emoji(self):
        """Opens dialogs to select an image, name it, and save it."""
        # 1. Select the image file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Reaction Image", "", 
            "Images (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        if not file_path:
            return # User canceled

        # 2. Ask for a custom name
        # Modern applications have beautiful, custom dialogs.
        # We will keep using this for simplicity, but it's the weak aesthetic point.
        name, ok = QInputDialog.getText(
            self, "Name Reaction", 
            "Enter a search name for this reaction:"
        )
        if not ok or not name.strip():
            return # User canceled or left blank
            
        name = name.strip()

        # 3. Copy the file into the project's images directory
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.images_dir, filename)

        try:
            # Copy the file. If it already exists there, it will just overwrite/update it.
            # Using shutil ensures it copies properly across drives/partitions on Windows.
            shutil.copy(file_path, dest_path)
        except shutil.SameFileError:
            pass # The user selected a file that is ALREADY inside the images folder

        # 4. Update JSON with a relative, OS-agnostic path
        # We enforce forward slashes '/' so the JSON works exactly the same on Windows and Linux
        # when we read it back.
        rel_path = f"images/{filename}"
        self.emoji_data[name] = rel_path
        self.save_data()

        # 5. Refresh the UI to show the new image
        self.populate_grid(self.search_bar.text())
        self.search_bar.clear() # Clear search so they can see their new addition

    def copy_to_clipboard(self, item):
        """Copies the clicked image to the OS clipboard."""
        image_path = item.data(Qt.ItemDataRole.UserRole)
        image = QImage(image_path)
        
        if image.isNull():
            QMessageBox.warning(self, "Error", "Failed to load image to clipboard.")
            return

        clipboard = QApplication.clipboard()
        clipboard.setImage(image)
        
        # Minimize the window after copying for a smoother workflow
        self.showMinimized()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Optional: If you have a custom font, you'd load it and set it globally here
    # app.setFont(QFont('Inter', 10))
    
    app.setQuitOnLastWindowClosed(True) 
    window = AestheticReactionBoard()
    window.show()
    sys.exit(app.exec())