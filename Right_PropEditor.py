import sys  
from PyQt6.QtCore import Qt  
from PyQt6.QtGui import QIcon  
from PyQt6.QtWidgets import (  
    QApplication, QWidget, QVBoxLayout,QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QFormLayout, QScrollArea, QGroupBox,QMessageBox
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator


import yaml
import yaml

class RightSection_BackEnd:
    def __init__(self, file_path):
        """
        Initialize the backend with the path to the YAML file.
        """
        self.file_path = file_path
        self.config_data = self.load_config()

    def load_config(self):
        """
        Load the configuration data from the YAML file.
        """
        try:
            with open(self.file_path, "r") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}

    def save_config(self):
        """
        Save the current configuration data back to the YAML file.
        The 'Groups' section will be preserved from the real config file.
        """
        # Load the real config file to preserve the 'Groups' section
        real_config_data = self.load_config()
        groups_data = real_config_data.get('Groups', {})

        # Create a copy of the current config data (without the 'Groups' section)
        config_data_to_save = self.config_data.copy()
        
        # Remove 'Groups' from the current config data to avoid overwriting it
        if 'Groups' in config_data_to_save:
            del config_data_to_save['Groups']

        # Add the preserved 'Groups' data back to the config data to save
        config_data_to_save['Groups'] = groups_data

        # Save the merged configuration to the YAML file
        with open(self.file_path, "w") as file:
            yaml.safe_dump(config_data_to_save, file)

    def get_section(self, section=None):
        """
        Retrieve a specific section of the configuration data.
        If no section is specified, return the entire configuration.
        """
        if not section:
            return self.config_data

        keys = section.split(".")
        data = self.config_data
        for key in keys:
            data = data.get(key, {})
        return data

    def update_value(self, path, value):
        """
        Update a value in the configuration data given a dot-separated path.
        """
        keys = path.split(".")
        self._set_nested_value(self.config_data, keys, value)

    def _set_nested_value(self, data, keys, value):
        """
        Helper function to set a value in a nested dictionary.
        """
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value

    def convert_to_type(self, value):
        """
        Convert a string value to its appropriate data type (e.g., int, float, bool).
        """
        try:
            return yaml.safe_load(value)
        except ValueError:
            return value


class ScrollableLineEdit(QLineEdit):
    def __init__(
        self,
        initial_value=0,
        min_value=-1000000,
        max_value=1000000,
        step=1,
        parent=None,
    ):
        super().__init__(parent)

        self._value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._step = step

        self.setText(str(self._value))

        if isinstance(initial_value, int):

            self.setValidator(QIntValidator(self._min_value, self._max_value))
        elif isinstance(initial_value, float):

            self.setValidator(QDoubleValidator(self._min_value, self._max_value, 16))

        self.setStyleSheet(
            """
                    QLineEdit {
                        padding: 4px;
                        font-size: 14px;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                    }
                    QLineEdit:focus {
                        border-color: #4CAF50;
                    }
                """
        )

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._can_scroll = False

    def focusInEvent(self, event):
        """
        Handle when the widget gains focus.
        """
        super().focusInEvent(event)
        self._can_scroll = True

    def focusOutEvent(self, event):
        """
        Handle when the widget loses focus.
        """
        super().focusOutEvent(event)
        self._can_scroll = False

    def wheelEvent(self, event):
        """
        Handle mouse wheel events to increase/decrease the value.
        """
        if self._can_scroll:
            delta = event.angleDelta().y() // 120
            new_value = self._value + delta * self._step
            new_value = max(self._min_value, min(self._max_value, new_value))
            self.setValue(new_value)

    def setValue(self, value):
        """
        Set the value of the widget and update the display text.
        Only 1 decimal place is shown for display.
        """
        if self._min_value <= value <= self._max_value:
            self._value = value

            self.setText(f"{self._value:.1f}")

    def value(self):
        """
        Retrieve the current value.
        """
        return self._value


class RightSection_Editor(QWidget):
    def __init__(self, backend, section=None):
        super().__init__()
        self.backend = backend
        self.section = section
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Config Editor")
        self.setWindowIcon(QIcon("icon.png"))

        self.layout = QHBoxLayout()

        self.group_box = QGroupBox("Configuration Settings")
        self.group_box.setStyleSheet(
            """
            QGroupBox {
                font-family: 'Arial', sans-serif;  /* Set the font family */
                font-size: 16px;  /* Set the font size */
                color: #333;  /* Set the title color */
                border: 1px solid #ccc;  /* Optional: add border */
                border-radius: 5px;  /* Optional: rounded corners */
                margin-top: 10px;  /* Add some margin at the top */
                padding: 5px;  /* Add padding around the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;  /* Position the title in the center */
                padding-left: 10px;  /* Add padding to the left of the title */
            }
        """
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumWidth(400)
        self.save_button = QPushButton("Save Changes")

        if __name__ == "__main__":
            self.edit_materials_button = QPushButton("Edit Materials")
            self.edit_properties_button = QPushButton("Edit Properties")

        self.group_layout = QFormLayout()

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.group_box)

        self.layout.addWidget(self.scroll_area)
        # self.layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)
        self.show()

        self.update_ui(self.section)

    def update_ui(self, section):
        """
        Updates the UI to display the correct section data.
        Clears the layout before creating the new section.
        """

        self.clear_layout(self.group_layout)

        section_data = self.backend.get_section(section)

        self.line_edits = {}
        self.create_line_edits(section_data, self.group_layout, section)

        self.group_box.setLayout(self.group_layout)

    def reload_config(self, new_file_path, section=None):
        """
        Reload the configuration from a new file path and update the UI.
        """

        self.backend = RightSection_BackEnd(new_file_path)

        self.section = section or self.section

        self.update_ui(self.section)

    def clear_layout(self, layout):
        """
        Clears all widgets from a given layout, including child layouts.
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def create_line_edits(self, data, parent_layout, path=""):
        """
        Recursive function that creates ScrollableLineEdits for each field in the data.
        Handles special sections like "Particles", "Sound", and dynamically detected sections like "DIRT", etc.
        """
        if isinstance(data, dict):
            particles_data = None
            sound_data = None
            dynamic_groups = []

            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key

                if key == "Particles":
                    particles_data = value
                elif key == "Sound":
                    sound_data = value
                elif isinstance(value, dict):
                    dynamic_groups.append((key, value))
                else:
                    self.create_line_edits(value, parent_layout, new_path)

            if particles_data is not None:
                self.create_groupbox_section(
                    "Particles", particles_data, parent_layout, f"{path}.Particles"
                )

            if sound_data is not None:
                self.create_groupbox_section(
                    "Sound", sound_data, parent_layout, f"{path}.Sound"
                )

            for group_name, group_data in dynamic_groups:
                self.create_groupbox_section(
                    group_name, group_data, parent_layout, f"{path}.{group_name}"
                )

        else:

            is_properties_section = "Properties" in self.section
            is_materials_section = "Materials" in self.section

            label = QLabel(path.split(".")[-1])
            label.setStyleSheet(
                """
                QLabel {
                    padding: 4px;
                    font-size: 14px;
                    border: 2px solid #000000; /* Green hollow outline */
                    background-color: #ADD8E6; /* Grey background color */
                    border-radius: 8px;       /* Rounded corners */
                    margin: 0px;
                    color: black;             /* Text color */
                    text-align: center;       /* Center the text */
                }
                QToolTip {
                    background-color: #333;
                    color: white;
                    border: 1px solid #888;
                    border-radius: 3px;
                }
            """
            )

            tooltip_key = path.split(".")[-1]

            tooltip = TOOLTIPS.get(tooltip_key, None)

            if tooltip:
                label.setToolTip(tooltip)
            else:
                label.setToolTip(f"No tooltip available for {tooltip_key}.")

            if is_properties_section:
                if "Particles" in path or "Sound" in path:
                    label.setFixedWidth(100)
                else:
                    label.setFixedWidth(416)
            elif is_materials_section:
                if "Particles" in path or "Sound" in path:
                    label.setFixedWidth(100)
                else:
                    label.setFixedWidth(250)
            else:
                label.setFixedWidth(10)

            if isinstance(data, bool):

                line_edit = QLineEdit()
                line_edit.setText("True" if data else "False")
                line_edit.setStyleSheet(
                    """
                    QLineEdit {
                        padding: 4px;
                        font-size: 14px;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        background-color: #f0f0f0;  /* Light grey */
                    }
                """
                )
                line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
                line_edit.setReadOnly(True)

                line_edit.setMouseTracking(False)

                def toggle_boolean(event):
                    current_value = line_edit.text()
                    if current_value == "True":
                        line_edit.setText("False")
                    else:
                        line_edit.setText("True")

                line_edit.mousePressEvent = toggle_boolean

                def prevent_double_click(event):
                    event.ignore()

                line_edit.mouseDoubleClickEvent = prevent_double_click
            else:

                if isinstance(data, int):
                    line_edit = ScrollableLineEdit(
                        initial_value=data,
                        min_value=-1000000,
                        max_value=1000000,
                        step=1,
                    )
                elif isinstance(data, float):
                    line_edit = ScrollableLineEdit(
                        initial_value=data,
                        min_value=-1000000.0,
                        max_value=1000000.0,
                        step=0.1,
                    )
                else:

                    line_edit = QLineEdit(str(data))
                    line_edit.setStyleSheet(
                        """
                        QLineEdit {
                            padding: 4px;
                            font-size: 14px;
                            border: 1px solid #ccc;
                            border-radius: 5px;
                        }
                        QLineEdit:focus {
                            border-color: #4CAF50;
                        }
                    """
                    )

            if "Particles" in path or "Sound" in path:
                line_edit.setFixedWidth(300)
            else:
                if is_properties_section:
                    line_edit.setFixedWidth(60)
                elif is_materials_section:
                    line_edit.setFixedWidth(200)
                else:
                    line_edit.setFixedWidth(10)

            parent_layout.addRow(label, line_edit)

            self.line_edits[path] = line_edit

    def create_groupbox_section(self, section_name, data, parent_layout, section_path):
        """
        This function creates a QGroupBox for special sections like "Particles", "Sound", or dynamically detected groups.
        """
        group_box = QGroupBox(section_name)
        group_layout = QFormLayout()

        self.create_line_edits(data, group_layout, section_path)

        group_box.setLayout(group_layout)
        parent_layout.addRow(group_box)

    def save_changes(self):
        """
        Save the current changes.
        """
        if not self.backend.file_path:

            QMessageBox.warning(
                self,
                "Error",
                "No configuration file loaded. Please load a config first.",
            )
            return

        try:

            for path, line_edit in self.line_edits.items():
                value = self.backend.convert_to_type(line_edit.text())
                self.backend.update_value(path, value)
                print(path)

            self.backend.save_config()

            QMessageBox.information(
                self, "Success", "Properties saved to config successfully."
            )

        except Exception as e:

            print(str(e))
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def resizeEvent(self, event):
        """
        Override the resizeEvent method to print the window size
        whenever the user resizes the window.
        """
        super().resizeEvent(event)
        new_size = self.size()

    def set_section(self, section):
        """
        Change the section being displayed and update the UI.
        Can be called externally to switch sections.
        """
        self.section = section
        self.update_ui(self.section)


TOOLTIPS = {
    "ExplosionRadius": (
        "Overrides the original explosion radius.\n\n"
        "- **Default**: 0.0 (keeps original radius).\n"
        "- **Range**: [0.0, ∞)\n"
        "- **>0.0**: Custom explosion radius."
    ),
    "ExplosionFactor": (
        "Multiplies the original explosion radius.\n\n"
        "- **Default**: 1.0 (keeps original radius).\n"
        "- **0.0**: Nullifies the explosion.\n"
        "- **>1.0**: Magnifies the explosion radius."
    ),
    "ReplaceOriginalExplosion": (
        "Determines whether the original explosion is replaced with a custom one.\n\n"
        "- **Default**: false.\n"
        "- **True**: Replaces the original explosion (some properties may be lost).\n"
        "- **False**: Only affects ExplodeAny calculations."
    ),
    "UnderwaterExplosionFactor": (
        "Adjusts the explosion radius underwater.\n\n"
        "- **Default**: 0.5 (reduces radius to half).\n"
        "- **Range**: [0.0, ∞)\n"
        "- **1.0**: No change underwater.\n"
        "- **>1.0**: Magnifies the underwater radius."
    ),
    "ExplosionDamageBlocksUnderwater": (
        "Determines whether explosions damage unmanaged vanilla blocks underwater.\n\n"
        "- **Default**: false.\n"
        "- **True**: Custom explosion damages blocks like stone and dirt."
    ),
    "ReplaceOriginalExplosionWhenUnderwater": (
        "Specifies whether the original explosion is replaced when underwater.\n\n"
        "- **Default**: true.\n"
        "- **True**: Replaces the explosion with a custom one.\n"
        "- **False**: Both original and custom explosions occur."
    ),
    "ExplosionRemoveWaterloggedStateFromNearbyBlocks": (
        "Allows explosions to remove the waterlogged state from nearby blocks.\n\n"
        "- **Default**: false.\n"
        "- **True**: Waterlogged blocks lose their waterlogged state."
    ),
    "ExplosionRemoveWaterloggedStateFromNearbyBlocksOnSurface": (
        "Applies ExplosionRemoveWaterloggedStateFromNearbyBlocks on surface explosions.\n\n"
        "- **Default**: true."
    ),
    "ExplosionRemoveWaterloggedStateFromNearbyBlocksUnderwater": (
        "Applies ExplosionRemoveWaterloggedStateFromNearbyBlocks to underwater explosions.\n\n"
        "- **Default**: true."
    ),
    "ExplosionRemoveNearbyWaterloggedBlocks": (
        "Removes nearby waterlogged blocks before the explosion.\n\n"
        "- **Default**: false.\n"
        "- **True**: Prioritizes this over waterlogged state removal."
    ),
    "ExplosionRemoveNearbyLiquids": (
        "Allows explosions to remove nearby liquids before detonating.\n\n"
        "- **Default**: false.\n"
        "- **True**: Liquids in the explosion area are removed."
    ),
    "PackDroppedItems": (
        "Packs dropped items into a single entity to reduce lag.\n\n"
        "- **Default**: false.\n"
        "- **True**: All dropped items spawn as one entity."
    ),
    "Particles": (
        "Specifies particle effects during explosions.\n\n"
        "- **Name**: Particle type (see Spigot Particle documentation).\n"
        "- **DeltaX/Y/Z**: Size of the particle cube.\n"
        "- **Amount**: Number of particles (higher values may reduce performance).\n"
        "- **Speed**: Particle speed (must be ≥0).\n"
        "- **Force**: Ensures particles are visible up to 256 blocks away.\n"
        "- **Color**: Applies only to REDSTONE particles.\n"
        "- **Size**: Particle size (applies to REDSTONE particles)."
    ),
    "Sound": (
        "Specifies sound effects during explosions.\n\n"
        "- **Name**: Sound type (see Spigot Sound documentation).\n"
        "- **Volume**: Adjusts sound radius.\n"
        "- **Pitch**: Speed of sound playback (range: 0.5–2.0)."
    ),
    "Damage": (
        "Base damage used to calculate effective block damage.\n\n"
        "- **Default**: Equal to BlockDurability.\n"
        "- **Range**: [0.0, ∞)\n"
        "- **0.0**: Block is unaffected by the explosion."
    ),
    "DropChance": (
        "Chance of a block dropping items naturally when broken.\n\n"
        "- **Default**: 0.0 (blocks never drop items).\n"
        "- **Range**: [0.0, 100.0]\n"
        "- **100.0**: Blocks always drop items."
    ),
    "DistanceAttenuationFactor": (
        "Controls how damage decreases with distance from the explosion.\n\n"
        "- **Default**: 0.0 (all blocks in range take equal damage).\n"
        "- **Range**: [0.0, 1.0]\n"
        "- **1.0**: Damage decreases linearly with distance."
    ),
    "UnderwaterDamageFactor": (
        "Adjusts damage taken by blocks underwater.\n\n"
        "- **Default**: 0.5 (halves underwater damage).\n"
        "- **Range**: [0.0, ∞)\n"
        "- **1.0**: Water has no effect.\n"
        "- **>1.0**: Magnifies underwater damage."
    ),
    "FancyUnderwaterDetection": (
        "Enables detailed water detection for underwater damage.\n\n"
        "- **Default**: false (checks water only at the explosion center).\n"
        "- **True**: Traces rays to detect water for each block."
    ),
    "Name": (
        "Specifies the name of the particles to be spawned during the explosion.\n\n"
        "- **Valid values**: Refer to Spigot Particle documentation for available types.\n"
        "- **Default**: REDSTONE."
    ),
    "DeltaX": (
        "Defines the size of the cube containing the particles along the X-axis.\n\n"
        "- **Default**: 2.0\n"
        "- **Higher values**: Larger spread of particles."
    ),
    "DeltaY": (
        "Defines the size of the cube containing the particles along the Y-axis.\n\n"
        "- **Default**: 2.0\n"
        "- **Higher values**: Larger spread of particles."
    ),
    "DeltaZ": (
        "Defines the size of the cube containing the particles along the Z-axis.\n\n"
        "- **Default**: 2.0\n"
        "- **Higher values**: Larger spread of particles."
    ),
    "Amount": (
        "Sets the number of particles to be spawned.\n\n"
        "- **Default**: 2000\n"
        "- **Caution**: Large values can cause performance issues like FPS drops."
    ),
    "Speed": (
        "Defines the speed of the particles.\n\n"
        "- **Default**: 1.0\n"
        "- **Higher values**: Faster particles."
    ),
    "Force": (
        "If true, the particles can be seen up to 256 blocks away.\n\n"
        "- **Default**: true."
    ),
    "Red": (
        "Sets the red component of the particle color.\n\n"
        "- **Default**: 255\n"
        "- **Valid range**: [0, 255]."
    ),
    "Blue": (
        "Sets the blue component of the particle color.\n\n"
        "- **Default**: 0\n"
        "- **Valid range**: [0, 255]."
    ),
    "Green": (
        "Sets the green component of the particle color.\n\n"
        "- **Default**: 255\n"
        "- **Valid range**: [0, 255]."
    ),
    "Size": (
        "Defines the size of the particles (only for REDSTONE particles).\n\n"
        "- **Default**: 2.0\n"
        "- **Higher values**: Larger particles."
    ),
    "Sound_Name": (
        "Specifies the sound to be played when the entity explodes.\n\n"
        "- **Valid values**: Refer to Spigot Sound documentation for available sounds.\n"
        "- **Default**: ENTITY_OCELOT_HURT."
    ),
    "Sound_Volume": (
        "Sets the volume of the explosion sound.\n\n"
        "- **Default**: 1.0\n"
        "- **Range**: [0.0, ∞). Higher values allow the sound to be heard from farther away."
    ),
    "Sound_Pitch": (
        "Defines the pitch (speed) of the explosion sound.\n\n"
        "- **Default**: 1.0\n"
        "- **Range**: [0.5, 2.0]."
    ),
}


if __name__ == "__main__":
    app = QApplication(sys.argv)

    config_file_path = "config.yaml"
    backend = RightSection_BackEnd(config_file_path)

    section_to_display = "VanillaEntity.Pinapple.Properties"  # Properties/Materials
    editor = RightSection_Editor(backend, section=section_to_display)

    sys.exit(app.exec())
