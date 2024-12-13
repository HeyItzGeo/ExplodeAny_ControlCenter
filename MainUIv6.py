import sys
import os
import yaml
from PyQt6.QtCore import Qt,QSize,QTimer
from PyQt6.QtGui import QAction,QColor,QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QComboBox, QTabWidget, QSplitter, QFrame, QListWidget, 
    QInputDialog, QAbstractItemView, QFileDialog,QMessageBox,QListWidgetItem,QScrollArea,QFormLayout,QToolButton
)
import Backend as backend
from Right_PropEditor import RightSection_Editor,RightSection_BackEnd

from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QBrush
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QListWidgetItem

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QRect


class IconOverlayDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        """Custom painting for the item."""
        painter.save()

        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon:
            icon_rect = option.rect
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(option.palette.text().color())

            font = QFont()
            font.setPointSize(16)
            painter.setFont(font)

            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.restore()


class GroupSelector(QWidget):
    """A widget for selecting groups with horizontal scrolling and wrapping."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group Selector")
        self.layout = QVBoxLayout()
        self.setup_ui()

    def setup_ui(self):
        """Set up the group selector with a label and group list."""

        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet(
            """
            border: 1px solid black;
            border-radius: 5px;
        """
        )
        self.main_layout = QVBoxLayout(self.main_frame)

        self.key_label = QLabel("Purple = Entity Group | Green = Block Group")
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_label.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            color: #444;
            margin-bottom: 5px;
        """
        )
        self.main_layout.addWidget(self.key_label)

        self.group_list = QListWidget()
        self.group_list.setFlow(QListWidget.Flow.LeftToRight)
        self.group_list.setWrapping(True)
        self.group_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.group_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.group_list.setSpacing(11)

        self.group_list.setItemDelegate(IconOverlayDelegate())

        self.main_layout.addWidget(self.group_list)

        self.layout.addWidget(self.main_frame)
        self.setLayout(self.layout)

        self.update_item_size()

    def update_item_size(self):
        """Update item sizes dynamically based on the widget size."""
        available_width = self.width()
        available_height = self.height()

        self.cols = max(1, available_width // 140)
        self.rows = max(3, available_height // 50)

        item_width = available_width // self.cols
        item_height = available_height // self.rows
        self.item_size = QSize(item_width, item_height)

        self.group_list.setIconSize(self.item_size)

        for index in range(self.group_list.count()):
            item = self.group_list.item(index)
            item.setSizeHint(self.item_size)

    def resizeEvent(self, event):
        """Handle resize events to dynamically update item sizes."""
        super().resizeEvent(event)
        self.update_item_size()

    def populate_groups(self, group_names, group_statuses=None):
        """Populate the group list with given group names and conditionally change their colors."""
        self.group_list.clear()

        self.group_list.setIconSize(self.item_size)

        for group in group_names:
            item = QListWidgetItem(group)
            item.setSizeHint(self.item_size)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if group_statuses and group in group_statuses:
                status = group_statuses[group]
                if status == "red":
                    pass
                else:

                    item.setBackground(QColor("#FFFFFF"))
                    icon_path = resource_path("Icons/GroupBlockIcon.svg")
                    icon = QIcon(icon_path)
                    
                    item.setIcon(icon)
            else:

                icon_path = resource_path("Icons/GroupEntityIcon.svg")
                icon = QIcon(icon_path)
                item.setIcon(icon)

            self.group_list.addItem(item)


def resource_path(relative_path):
    """Get the absolute path to the resource, works for both development and frozen exe."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS when running the bundled .exe
        base_path = sys._MEIPASS
    except Exception:
        # Fallback to the current working directory in development
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

from PyQt6.QtWidgets import QFrame


class ConfigSection(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")

        self.layout = QVBoxLayout()
        self.setup_ui()

    def setup_ui(self):

        self.entity_group_label = QLabel("Entity Group Name")
        self.entity_group_entry = QLineEdit()
        self.block_group_label = QLabel("Block Group Name")
        self.block_group_entry = QLineEdit()

        self.entity_particles_checkbox = QCheckBox("Entity Particles")
        self.block_particles_checkbox = QCheckBox("Block Particles")
        self.entity_sounds_checkbox = QCheckBox("Entity Sounds")
        self.block_sounds_checkbox = QCheckBox("Block Sounds")

        self.entity_particles_checkbox.setChecked(True)
        self.block_particles_checkbox.setChecked(True)
        self.entity_sounds_checkbox.setChecked(True)
        self.block_sounds_checkbox.setChecked(True)

        self.add_group_button = QPushButton("Add Group(s) to config.")

        self._apply_styles()

        self._setup_layout()

    def _setup_layout(self):
        entry_layout = QHBoxLayout()
        entity_layout = QVBoxLayout()
        block_layout = QVBoxLayout()

        entity_layout.addWidget(self.entity_group_label)
        entity_layout.addWidget(self.entity_group_entry)

        block_layout.addWidget(self.block_group_label)
        block_layout.addWidget(self.block_group_entry)

        entry_layout.addLayout(entity_layout)
        entry_layout.addLayout(block_layout)

        checkbox_layout = QHBoxLayout()

        entity_frame = QFrame()
        entity_frame.setLayout(QHBoxLayout())
        entity_frame.layout().addWidget(self.entity_particles_checkbox)
        entity_frame.layout().addWidget(self.entity_sounds_checkbox)
        entity_frame.setStyleSheet("border: 1px solid black;")

        block_frame = QFrame()
        block_frame.setLayout(QHBoxLayout())
        block_frame.layout().addWidget(self.block_particles_checkbox)
        block_frame.layout().addWidget(self.block_sounds_checkbox)
        block_frame.setStyleSheet("border: 1px solid black;")

        checkbox_layout.addWidget(entity_frame)
        checkbox_layout.addWidget(block_frame)

        self.layout.addLayout(entry_layout)
        self.layout.addLayout(checkbox_layout)
        self.layout.addWidget(self.add_group_button)

        self.group_selector = GroupSelector()
        self.layout.addWidget(self.group_selector)

        self.setLayout(self.layout)

    def _apply_styles(self):

        self.entity_group_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        """
        )
        self.block_group_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        """
        )

        self.entity_group_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.block_group_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.entity_group_entry.setStyleSheet(
            """
            padding: 5px;
            border-radius: 4px;
            border: 1px solid #ccc;
            background-color: #fff;
            font-size: 14px;
        """
        )
        self.block_group_entry.setStyleSheet(
            """
            padding: 5px;
            border-radius: 4px;
            border: 1px solid #ccc;
            background-color: #fff;
            font-size: 14px;
        """
        )

        self.entity_particles_checkbox.setStyleSheet(
            """
            border: none; 
            font-size: 14px;
            color: #333;
            margin-right: 15px;
        """
        )
        self.block_particles_checkbox.setStyleSheet(
            """
            border: none; 
            font-size: 14px;
            color: #333;
        """
        )
        self.entity_sounds_checkbox.setStyleSheet(
            """
            border: none; 
            font-size: 14px;
            color: #333;
            margin-right: 15px;
        """
        )
        self.block_sounds_checkbox.setStyleSheet(
            """
            border: none; 
            font-size: 14px;
            color: #333;
        """
        )

        self.add_group_button.setStyleSheet(
            """
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        """
        )

    def highlight_entry(self, entry):
        original_stylesheet = entry.styleSheet()

        def flash():
            entry.setStyleSheet(
                """
                background-color: lightyellow;
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #ccc;
                font-size: 14px;
            """
            )
            QTimer.singleShot(500, lambda: entry.setStyleSheet(original_stylesheet))

        flash()
        QTimer.singleShot(1000, flash)
        QTimer.singleShot(1500, flash)

    def get_group_selector(self):
        """Return the GroupSelector instance."""
        return self.group_selector

    def clear_groups(self):
        """Clear all groups from the GroupSelector."""
        self.group_selector.populate_groups([])


class EntityBlockSection(QWidget):
    """Handles the section for editing and viewing entities and blocks (bottom part)."""

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")

        self.layout = QVBoxLayout()

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI components."""

        self.entity_tab_widget = QTabWidget()
        self.block_tab_widget = QTabWidget()

        self.add_entity_button = QPushButton("Add Entity")
        self.add_block_button = QPushButton("Add Block")
        self.remove_button = QPushButton("Remove Selected")

        self.entity_list_widget = QListWidget()
        self.entity_list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.block_list_widget = QListWidget()
        self.block_list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        self._setup_layout()

    def _setup_layout(self):
        """Sets up the layout of the widget."""

        entity_tab = QWidget()

        entity_layout = QVBoxLayout()
        entity_layout.addWidget(self.add_entity_button)
        entity_layout.addWidget(self.entity_list_widget)
        entity_tab.setLayout(entity_layout)
        self.entity_tab_widget.addTab(entity_tab, "Entities")

        block_tab = QWidget()
        block_layout = QVBoxLayout()
        block_layout.addWidget(self.add_block_button)
        block_layout.addWidget(self.block_list_widget)
        block_tab.setLayout(block_layout)
        self.block_tab_widget.addTab(block_tab, "Blocks")

        side_by_side_layout = QHBoxLayout()

        side_by_side_layout.addWidget(self.entity_tab_widget)
        side_by_side_layout.addWidget(self.block_tab_widget)

        self.layout.addLayout(side_by_side_layout)
        self.layout.addWidget(self.remove_button)

        self.setLayout(self.layout)

    def update_tab_title(self, tab_widget, index, title):
        """
        Dynamically update the title of a tab.

        Args:
            tab_widget (QTabWidget): The tab widget (either entity_tab_widget or block_tab_widget).
            index (int): The index of the tab to update.
            title (str): The new title for the tab.
        """
        tab_widget.setTabText(index, title)


class MiddleSection(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.layout = QVBoxLayout()

        self.config_section = ConfigSection()
        self.entity_block_section = EntityBlockSection()

        self.layout.addWidget(self.config_section)
        # self.layout.addSpacing(20)

        self.layout.addWidget(self.entity_block_section)

        self.setLayout(self.layout)


class RightSection(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dynamic Config Viewer")

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.backend = RightSection_BackEnd("")
        self.config_editor = RightSection_Editor(self.backend, section="")
        self.layout.addWidget(self.config_editor)

        self.switch_button = QPushButton("Save Changes")
        self.switch_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        self.switch_button.clicked.connect(self.trigger_save)
        self.layout.addWidget(self.switch_button)

    def trigger_save(self):
        if self.config_editor:

            self.config_editor.save_changes()

    def get_config_editor(self):
        """Expose the config_editor instance."""
        return self.config_editor

    def PassToReload(self, groupName, File_Path):

        section_path = f"VanillaEntity.{groupName}.Materials"
        print(section_path)
        self.config_editor.reload_config(File_Path, section=section_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = {}

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.setGeometry(
            screen_geometry.width() // 8,
            screen_geometry.height() // 8,
            int(screen_geometry.width() // 1.5),
            int(screen_geometry.height() // 1.5),
        )

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        middle_section = MiddleSection()
        right_section = RightSection()

        main_splitter.addWidget(middle_section)
        main_splitter.addWidget(right_section)

        main_splitter.setSizes([1, 1])

        self.setCentralWidget(main_splitter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
