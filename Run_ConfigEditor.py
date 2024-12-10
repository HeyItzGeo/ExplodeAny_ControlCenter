import sys
from PyQt6.QtWidgets import QApplication, QMessageBox,QComboBox, QDialogButtonBox,QDialog,QLineEdit,QLabel, QWidget,QMenuBar, QVBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QInputDialog, QPushButton,QFileDialog,QFormLayout
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction,QIcon,QColor,QFont
import MainUIv6 as UI
import Backend as backend
import yaml
import Right_PropEditor as RightSection



class AddEntityDialog(QDialog):
    def __init__(self, allowed_entity_values, item_type="Entity", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add {item_type}")
        self.selected_entity = None
        self.entered_text = None
        self.item_type = item_type  

        
        layout = QVBoxLayout(self)

        
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(f"Custom {self.item_type} Name")
        layout.addWidget(QLabel(f"Enter {self.item_type} Name:"))
        layout.addWidget(self.line_edit)

        if allowed_entity_values:  
            
            self.combo_box = QComboBox(self)
            self.combo_box.addItem(f"Custom {self.item_type}")  
            self.combo_box.addItems(allowed_entity_values)  
            self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)
            layout.addWidget(QLabel(f"Or pick from the {self.item_type} List below:"))
            layout.addWidget(self.combo_box)

        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def on_combo_box_changed(self, index):
        """Enable or disable the line edit based on the selected combo box option."""
        if self.combo_box.itemText(index) == f"Custom {self.item_type}":
            self.line_edit.setEnabled(True)
        else:
            self.line_edit.setEnabled(False)

    def get_data(self):
        """
        Returns the entered text or the selected item.
        If 'Custom {item_type}' is selected, use the text from the line edit.
        """
        if hasattr(self, 'combo_box') and self.combo_box.currentText() == f"Custom {self.item_type}":
            self.entered_text = self.line_edit.text().strip()
            if self.entered_text:
                # Split input by commas if multiple values
                return [name.strip() for name in self.entered_text.split(',')]
            return None
        return self.combo_box.currentText() if hasattr(self, 'combo_box') else self.line_edit.text().strip()


class MainInputOutput:
    def __init__(self, window):
        self.window = window
        self.config_manager = None 
        self.selected_entity_group = None 
        self.selected_block_group = None
        self.setup_connections()
        self.create_file_menu()
    def setup_connections(self):
        """Set up all button and item connections."""
        # MiddleSection connections
        middle_section = self.window.findChild(UI.MiddleSection)
        if middle_section:

            # Connect add_group_button to on_Add_Group
            self.connect_button_action(middle_section.config_section.add_group_button, self.on_Add_Group, middle_section)
            
            
            # Connect group list item click to handle_group_selection
            group_selector = middle_section.config_section.get_group_selector()
            self.connect_item_clicked_action(group_selector.group_list, self.handle_group_selection, group_selector)
            
        # EntityBlockSection connections
        entity_block_section = self.window.findChild(UI.EntityBlockSection)
        if entity_block_section:
            # Connect add/remove buttons
            self.connect_button_action(entity_block_section.add_entity_button, self.add_entity, entity_block_section.entity_list_widget)
            self.connect_button_action(entity_block_section.add_block_button, self.add_block, entity_block_section.block_list_widget)
            self.connect_button_action(entity_block_section.remove_button, self.remove_selected, entity_block_section.entity_list_widget, entity_block_section.block_list_widget)
    def create_file_menu(self):
        """Create the file menu with 'Empty Config' and 'Load YAML' options."""
        menu_bar = self.window.menuBar()  # Access the menu bar from the window

        file_menu = menu_bar.addMenu("File")

        # Create 'Empty Config' and 'Load YAML' actions
        empty_config_action = QAction("Empty_Config...", self.window)
        load_yaml_action = QAction("Load YAML...", self.window)

        file_menu.addAction(empty_config_action)
        file_menu.addAction(load_yaml_action)

        # Connect actions to respective slots
        empty_config_action.triggered.connect(self.on_Empty_Load)
        load_yaml_action.triggered.connect(self.on_load_yaml)
    

    @staticmethod
    def connect_button_action(button, action, *args):
        """Generalized function to connect a button's click signal to a slot."""
        button.clicked.connect(lambda: action(*args))

    @staticmethod
    def connect_item_clicked_action(list_widget, action, *args):
        """Generalized function to connect an item click signal to a slot."""
        list_widget.itemClicked.connect(lambda item: action(item, *args))

    def on_Add_Group(self, middle_section):
        """Handle the addition of a new group by calling the backend."""
        
        
        

        # Check if config_manager is properly loaded
        if not self.config_manager :
            QMessageBox.warning(self.window, "Configuration Error", "Please load a configuraaaaation file first.")
            return
            
        # Retrieve text from QLineEdit widgets
        EntityText = middle_section.config_section.entity_group_entry.text()
        BlockText = middle_section.config_section.block_group_entry.text()

        # Validate the inputs
        if not EntityText or not BlockText:
            QMessageBox.warning(self.window, "Input Error", "Both Entity and Block group names must be provided.")
            
            # Directly check if there is text and highlight accordingly
            if not middle_section.config_section.entity_group_entry.text():
                middle_section.config_section.highlight_entry(middle_section.config_section.entity_group_entry)
            
            if not middle_section.config_section.block_group_entry.text():
                middle_section.config_section.highlight_entry(middle_section.config_section.block_group_entry)

            return
        
        # Check if Entity and Block names are the same
        if EntityText == BlockText:
            QMessageBox.warning(self.window, "Input Error", "Entity and Block group names cannot be the same.")
            return

        # Get checkbox states
        entity_particles_checked = middle_section.config_section.entity_particles_checkbox.isChecked()
        block_particles_checked = middle_section.config_section.block_particles_checkbox.isChecked()
        entity_sounds_checked = middle_section.config_section.entity_sounds_checkbox.isChecked()
        block_sounds_checked = middle_section.config_section.block_sounds_checkbox.isChecked()

        try:
            # Call the backend Add_Group_Pairs function with checkbox states
            backend.Add_Group_Pairs(
                self.config_manager,
                EntityText,
                BlockText,
                entity_particles_checked,
                block_particles_checked,
                entity_sounds_checked,
                block_sounds_checked
            )
            QMessageBox.information(self.window, "Success", f"Group '{EntityText}' and Block '{BlockText}' added successfully.")
            
            # Optionally, you can refresh or update the UI after this operation
            group_selector = middle_section.config_section.get_group_selector()
            if group_selector:
                # Update the group list (optional: reload groups from config_manager)
                groups = self.config_manager.get_value('Groups')
                if groups:
                    group_selector.populate_groups(list(groups.keys()))
                    
                    middle_section.config_section.block_group_entry.clear()
                    middle_section.config_section.entity_group_entry.clear()
                    
                    self.reload_yaml()  # This will reload the same file you previously loaded
                                        # Manually trigger the group selection for the first two items if available
                    if len(groups) >= 2:
                        item1 = group_selector.group_list.item(0)  # First item
                        item2 = group_selector.group_list.item(1)  # Second item

                        # Ensure the items are valid before selecting
                        if item1:
                            self.handle_group_selection(item1, group_selector)
                        if item2:
                            self.handle_group_selection(item2, group_selector)

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"An error occurred while adding the group: {e}")
            print(f"Error in on_Add_Group: {e}")



    def handle_group_selection(self, item, group_selector):
        """Handle the group selection in the main program."""
        selected_group = item.text()

        try:
            if self.config_manager:  # Ensure config_manager is loaded
                Right_Section_Instance = self._get_right_section_instance()  # Separate logic to get Right_Section_Instance
                if Right_Section_Instance:
                    
                    config_editor_instance = Right_Section_Instance.get_config_editor()

                    # Check if the selected group is an Entity or Block
                    if selected_group in self.entity_to_block:
                        # It's an Entity Group
                        self._handle_entity_group(selected_group, config_editor_instance)

                    elif selected_group in self.block_to_entity:
                        # It's a Block Group
                        self._handle_block_group(selected_group, config_editor_instance)

                    else:
                        # Display an error message to the user
                        QMessageBox.warning(
                            group_selector,  # Parent window/widget
                            "Invalid VanillaEntity",  # Title
                            f"Invalid VanillaEntity: '{selected_group}' not connected to anything.",  # Message
                            QMessageBox.StandardButton.Ok  # Buttons
                        )
                else:
                    raise ValueError("Right_Section_Instance not found.")

            else:
                raise ValueError("Config manager not loaded yet.")

        except Exception as e:
            print(f"Error retrieving group items: {e}")
            QMessageBox.critical(group_selector, "Error", "An error occurred while retrieving group items.")

    def _get_right_section_instance(self):
        """Retrieve the Right Section Instance."""
        return self.window.findChild(UI.RightSection)

    def _handle_entity_group(self, selected_group, config_editor_instance):
        """Handle entity group selection."""
        entity_block_section = self.window.findChild(UI.EntityBlockSection)
        if entity_block_section:
            entity_list_widget = entity_block_section.entity_list_widget
            entity_list_widget.clear()  # Clear current list
            
            entity_block_section.update_tab_title(entity_block_section.entity_tab_widget, 0, f"Entity: {selected_group}")


            # Store the selected entity group
            self.selected_entity_group = selected_group
            

            # Retrieve items for the entity group
            group_items = backend.retrieve_group_items(self.config_manager, selected_group)
            if group_items:
                for item in group_items:
                    entity_list_widget.addItem(item)
                print(f"Added {len(group_items)} items to the entity list.")
            else:
                entity_list_widget.addItem("Empty")
                print(f"No items found for entity group '{selected_group}'. Added 'Empty' placeholder.")

        config_editor_instance.reload_config(self.file_path, section=f"VanillaEntity.{self.selected_entity_group}.Properties")
        Title = f"Editing Group: {self.selected_entity_group}"
        config_editor_instance.group_box.setTitle(Title)

    def _handle_block_group(self, selected_group, config_editor_instance):
        """Handle block group selection."""
        entity_block_section = self.window.findChild(UI.EntityBlockSection)
        if entity_block_section:
            block_list_widget = entity_block_section.block_list_widget
            block_list_widget.clear()  # Clear current list
            
            entity_block_section.update_tab_title(entity_block_section.block_tab_widget, 0, f"Block: {selected_group}")


            # Store the selected block group
            self.selected_block_group = selected_group
            

            # Retrieve items for the block group
            group_items = backend.retrieve_group_items(self.config_manager, selected_group)
            if group_items:
                for item in group_items:
                    block_list_widget.addItem(item)
                print(f"Added {len(group_items)} items to the block list.")
            else:
                block_list_widget.addItem("Empty")
                print(f"No items found for block group '{selected_group}'. Added 'Empty' placeholder.")

        if selected_group in self.block_to_entity:
            # Find the paired entity for the selected block group
            paired_entity = self.block_to_entity.get(selected_group)
            if not paired_entity:
                raise ValueError(f"No paired entity found for block group: {selected_group}")

            # Construct the section path using the paired entity
            section_path = f"VanillaEntity.{paired_entity}.Materials"

            # Reload the configuration
            config_editor_instance.reload_config(self.file_path, section=section_path)
            Title = f"Editing Group: {selected_group}"
            config_editor_instance.group_box.setTitle(Title)


    def add_entity(self, entity_list_widget: QListWidget):
        # Check if config_manager is initialized
        if not self.config_manager or not self.config_manager.get_value('Groups'):
            QMessageBox.warning(None, "Error", "No config loaded. Cannot add entity.")
            return
        allowed_entity_values = [
                     "PRIMED_TNT", "ENDER_CRYSTAL","WITHER", "MINECART_TNT", "CREEPER", 
                    "CHARGED_CREEPER", "FIREBALL", "DRAGON_FIREBALL", "SMALL_FIREBALL",
                    "WITHER_SKULL", "CHARGED_WITHER_SKULL", "BED", "RESPAWN_ANCHOR"
                ]

        # Open the custom dialog for adding an entity
        dialog = AddEntityDialog(allowed_entity_values, item_type="Entity")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entity_input = dialog.get_data()
            if entity_input:
                if isinstance(entity_input, list):
                    # Remove the "Empty" placeholder if present
                    for i in range(entity_list_widget.count()):
                        if entity_list_widget.item(i).text() == "Empty":
                            entity_list_widget.takeItem(i)
                            break

                    # Add each new entity to the list widget
                    for entity_name in entity_input:
                        entity_list_widget.addItem(entity_name)
                    if self.selected_entity_group:
                        
                        self.config_manager.add_items_to_group(self.selected_entity_group, entity_input)
                        print(f"Added entities {', '.join(entity_input)} to the '{self.selected_entity_group}' entity group.")
                    else:
                        print("No entity group selected. Cannot add entity.")
                else:
                    
                    entity_name = entity_input
                    # Remove the "Empty" placeholder if present
                    for i in range(entity_list_widget.count()):
                        if entity_list_widget.item(i).text() == "Empty":
                            entity_list_widget.takeItem(i)
                            break
                    entity_list_widget.addItem(entity_name)

                    
                    if self.selected_entity_group:
                        self.config_manager.add_items_to_group(self.selected_entity_group, [entity_name])
                        print(f"Added '{entity_name}' to the '{self.selected_entity_group}' entity group.")
                    else:
                        print("No entity group selected. Cannot add entity.")

    def add_block(self, block_list_widget):
        """Prompt the user to add a block using AddEntityDialog."""
        
        # Check if config_manager is initialized
        if not self.config_manager or not self.config_manager.get_value('Groups'):
            QMessageBox.warning(None, "Error", "No config loaded. Cannot add block.")
            return

       
        dialog = AddEntityDialog({}, item_type="Block") 
        if dialog.exec() == QDialog.DialogCode.Accepted:
            block_input = dialog.get_data()
            if block_input:
                block_names = [name.strip() for name in block_input.split(',')]
                for i in range(block_list_widget.count()):
                    if block_list_widget.item(i).text() == "Empty":
                        block_list_widget.takeItem(i)
                        break

                # Add the new blocks to the list widget
                for block_name in block_names:
                    block_list_widget.addItem(block_name)

                # Ensure the selected block group is set
                if self.selected_block_group:
                    # Prepare the items to be added to the group
                    self.config_manager.add_items_to_group(self.selected_block_group, block_names)
                    print(f"Added blocks {', '.join(block_names)} to the '{self.selected_block_group}' block group.")
                else:
                    print("No block group selected. Cannot add block.")



    def remove_selected(self, entity_list_widget, block_list_widget):
        """Remove the selected entities or blocks."""

        for widget in (entity_list_widget, block_list_widget):
            selected_items = widget.selectedItems()

            if widget == entity_list_widget:
                group = self.selected_entity_group
            elif widget == block_list_widget:
                group = self.selected_block_group

            for item in selected_items:
                widget.takeItem(widget.row(item))  
                print(f"Removing {item.text()} from group {group}")
                self.config_manager.remove_item_from_group(group, item.text()) 



    def on_Empty_Load(self):
        """Prompt the user for a file save location and create an empty configuration file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Create New Config File",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)",
        )


        if file_path:
            try:
                # Default content for the new configuration
                default_content = {
                    "UseBlockDatabase": False,
                    "CheckBlockDatabaseAtStartup": False,
                    "BlockDurability": 100.0,
                    "EnableMetrics": True,
                    "Checktool": {
                        "AlwaysEnabled": False,
                        "EnabledByDefault": False,
                        "PreventActionWhenCheckingHandledBlocks": True,
                        "PreventActionWhenCheckingNonHandledBlocks": True,
                        "SilentWhenCheckingOnDisabledWorlds": False,
                        "SilentWhenCheckingWithoutPermissions": False,
                        "SilentWhenCheckingNonHandledBlocks": False,
                        "SilentWhenCheckingHandledBlocks": False,
                        "ShowBossBar": False,
                        "BossBarColor": "PURPLE",
                        "BossBarStyle": "SOLID",
                        "BossBarDuration": 30
                    },
                    "Groups": {},
                    "VanillaEntity": {},
                    "Locale": {
                        "NotAllowed": "You are not allowed to perform this action!",
                        "Usage": "Usage: %DESCRIPTION%",
                        "OnlyPlayerAllowed": "Only players can perform this action!",
                        "PlayerDoesntExist": "Player %NAME% doesn't exist in the server!",
                        "PlayerIsOffline": "Player %NAME% must be online to perform that",
                        "EnterChecktoolMode": "You can now right-click a block with %PRETTY_ITEM% to display block durability",
                        "LeaveChecktoolMode": "You can no longer check for a block durability",
                        "ChecktoolToggledOn": "Checktool mode toggled on for player %NAME%",
                        "ChecktoolToggledOff": "Checktool mode toggled off for player %NAME%",
                        "ChecktoolUse": "Block health: %DURABILITY_PERCENTAGE%% (%PRETTY_MATERIAL%)",
                        "ChecktoolUseBossBar": "%PRETTY_MATERIAL%: %DURABILITY_PERCENTAGE%%",
                        "ChecktoolSet": "Checktool successfully set to %PRETTY_ITEM%!",
                        "ChecktoolNotPersisted": "Checktool item was set to %PRETTY_ITEM%, but it couldn't be persisted",
                        "ChecktoolGiven": "A checktool (%PRETTY_ITEM%) was given to player %NAME%",
                        "ChecktoolReset": "Checktool successfully reset to bare hand (Air)",
                        "ChecktoolNotHandled": "%PRETTY_MATERIAL% is not handled by the current configuration",
                        "ChecktoolInfo": "Current checktool item: %PRETTY_ITEM%",
                        "ChecktoolAlwaysEnabled": "Checktool can't be toggled off",
                        "DisabledInThisWorld": "This functionality is disabled in this world",
                        "Reloaded": "Reloaded successfully!",
                        "DebugEnabled": "Debug mode has been enabled",
                        "DebugDisabled": "Debug mode has been disabled"
                    },
                    "LocalePrefix": "[ExplodeAny]",
                    "DisabledWorlds": []
                }


                # Save the empty configuration to the specified path
                with open(file_path, "w") as file:
                    yaml.dump(default_content, file, default_flow_style=False)

                # Store the file path and initialize the config manager
                self.file_path = file_path
                self.config_manager = backend.YAMLConfigManager()
                self.config_manager.load_yaml(file_path)
                
                file_name = file_path.split("/")[-1]  # Get the file name from the path
                self.window.setWindowTitle(f"YAMLConfigManager - ExplodeAny - {file_name}")

                # Initialize mappings
                self.entity_to_block = {}
                self.block_to_entity = {}

                # Update the UI to reflect the empty configuration
                middle_section = self.window.findChild(UI.MiddleSection)
                if middle_section:
                    group_selector = middle_section.config_section.get_group_selector()
                    if group_selector:
                        group_selector.group_list.clear()  # Clear existing items
                        QMessageBox.information(
                            self.window,
                            "Empty Config Created",
                            f"An empty configuration file was created at:\n{file_path}",
                        )

                # Initialize the right section (if applicable)
                Right_Section_Instance = self._get_right_section_instance()
                if Right_Section_Instance:
                    config_editor_instance = Right_Section_Instance.get_config_editor()
                    if config_editor_instance:
                        # Use the correct parameter name
                        config_editor_instance.clear_layout(config_editor_instance.group_layout)
                        config_editor_instance.group_box.setTitle("New Config: Add Entity & Block Group Names")




                # Additional code to handle the entity and block list sections
                entity_block_section = self.window.findChild(UI.EntityBlockSection)
                if entity_block_section:
                    # Clear the current entity list
                    entity_list_widget = entity_block_section.entity_list_widget
                    entity_list_widget.clear()  # Clear current list

                    # Clear the current block list
                    block_list_widget = entity_block_section.block_list_widget
                    block_list_widget.clear()  # Clear current list

                    # Update tab titles for entity and block sections
                    entity_block_section.update_tab_title(entity_block_section.entity_tab_widget, 0, "Entity Group")
                    entity_block_section.update_tab_title(entity_block_section.block_tab_widget, 0, "Block Group")



            except Exception as e:
                QMessageBox.critical(
                    self.window,
                    "Error Creating Config",
                    f"An error occurred while creating the empty configuration: {e}",
                )
                print(f"Error in on_Empty_Load: {e}")
        else:
            QMessageBox.information(self.window, "Operation Canceled", "No file location was selected.")

    def reload_yaml(self):
        """Reload the YAML file using the stored file path."""
        if hasattr(self, 'file_path') and self.file_path:
            try:
                # Reload the file using the same file path
                self.config_manager.load_yaml(self.file_path)

                # Reinitialize mappings (optional)
                self.entity_to_block = {}
                self.block_to_entity = {}

                # Parse VanillaEntity section again
                vanilla_entity = self.config_manager.get_value('VanillaEntity', default={})
                groups = self.config_manager.get_value('Groups', default={})

                # Only clear the lists if both Groups and VanillaEntity are empty
                if not vanilla_entity and not groups:
                    # Clear entity and block lists if both are empty
                    entity_block_section = self.window.findChild(UI.EntityBlockSection)
                    if entity_block_section:
                        entity_list_widget = entity_block_section.entity_list_widget
                        block_list_widget = entity_block_section.block_list_widget
                        entity_list_widget.clear()
                        block_list_widget.clear()
                        

                # Handle VanillaEntity data mapping
                if vanilla_entity:
                    for entity_group, data in vanilla_entity.items():
                        materials = data.get('Materials', {})
                        for block_group in materials.keys():
                            # Map entity to block and vice versa
                            self.entity_to_block[entity_group] = block_group
                            self.block_to_entity[block_group] = entity_group

                # Reorder the groups based on entity_to_block
                ordered_groups = {}

                # First, populate the ordered_groups dictionary by following the order of self.entity_to_block
                for entity_group, block_group in self.entity_to_block.items():
                    # Ensure the block_group exists in groups
                    if entity_group in groups:
                        ordered_groups[entity_group] = groups[entity_group]

                    # Ensure the block_group also gets added in the right order
                    if block_group in groups and block_group not in ordered_groups:
                        ordered_groups[block_group] = groups[block_group]

                # Add any remaining groups that were not in entity_to_block
                for group_key, group_data in groups.items():
                    if group_key not in ordered_groups:
                        ordered_groups[group_key] = group_data

                # Repopulate Groups with the ordered groups
                middle_section = self.window.findChild(UI.MiddleSection)
                if middle_section:
                    group_selector = middle_section.config_section.get_group_selector()
                    if ordered_groups:  # Only populate if ordered groups are not empty
                        group_selector.populate_groups(ordered_groups, self.block_to_entity)
                    else:
                        print("No groups found in the YAML file.")

            except Exception as e:
                QMessageBox.critical(self.window, "Error", f"An error occurred while reloading the YAML file: {e}")
                print(f"Error reloading YAML: {e}")
        else:
            QMessageBox.warning(self.window, "File Error", "No YAML file loaded to reload.")

    def on_load_yaml(self):
        """Open file dialog to load a YAML file and populate groups using YAMLConfigManager."""
        # Open file dialog to select a YAML file
        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Open YAML File", "", "YAML Files (*.yaml *.yml);;All Files (*)", options=options
        )

        if file_path:
            try:
                # Store the file path to use later for reloading
                self.file_path = file_path  # Store the path in an instance attribute

                # Create an instance of the YAMLConfigManager and assign it to self.config_manager if not already initialized
                if not self.config_manager:
                    self.config_manager = backend.YAMLConfigManager()

                # Load the YAML file
                self.config_manager.load_yaml(file_path)
                # Update the window title with the file path
                file_name = file_path.split("/")[-1]  # Get the file name from the path
                self.window.setWindowTitle(f"YAMLConfigManager - ExplodeAny - {file_name}")


                # Initialize mappings
                self.entity_to_block = {}
                self.block_to_entity = {}

                # Load sections and use empty dictionaries as defaults
                vanilla_entity = self.config_manager.get_value("VanillaEntity", default={})
                groups = self.config_manager.get_value("Groups", default={})

                # Parse VanillaEntity section
                if vanilla_entity:
                    for entity_group, data in vanilla_entity.items():
                        materials = data.get("Materials", {})
                        for block_group in materials.keys():
                            # Map entity to block and vice versa
                            self.entity_to_block[entity_group] = block_group
                            self.block_to_entity[block_group] = entity_group

                # Reorder the groups based on entity_to_block
                ordered_groups = {}

                # First, populate the ordered_groups dictionary by following the order of self.entity_to_block
                for entity_group, block_group in self.entity_to_block.items():
                    # Ensure the entity_group and block_group exist in groups
                    if entity_group in groups:
                        ordered_groups[entity_group] = groups[entity_group]
                    if block_group in groups and block_group not in ordered_groups:
                        ordered_groups[block_group] = groups[block_group]

                # Add any remaining groups that were not in entity_to_block
                for group_key, group_data in groups.items():
                    if group_key not in ordered_groups:
                        ordered_groups[group_key] = group_data

                # Now, populate the group list in the correct order
                middle_section = self.window.findChild(UI.MiddleSection)
                if middle_section:
                    group_selector = middle_section.config_section.get_group_selector()
                    if group_selector:
                        # Clear the existing group list before repopulating
                        group_selector.group_list.clear()

                        # Repopulate the group list with new groups from ordered_groups
                        for group_name in ordered_groups.keys():
                            # Create a new QListWidgetItem for each group
                            item = QListWidgetItem(group_name)
                            # Add the styled item to the group list
                            group_selector.group_list.addItem(item)

                        # Force the widget to redraw (optional)
                        group_selector.group_list.update()

                        # Clear any previous block group entry
                        middle_section.config_section.block_group_entry.clear()

                        # Manually trigger the group selection for the first two items if available
                        if len(ordered_groups) >= 2:
                            # Get the first two items from ordered_groups
                            item1 = group_selector.group_list.item(0)  # First item
                            item2 = group_selector.group_list.item(1)  # Second item

                            # Ensure the items are valid before selecting
                            if item1:
                                self.handle_group_selection(item1, group_selector)
                            if item2:
                                self.handle_group_selection(item2, group_selector)

                        # Reload the YAML after populating groups
                        self.reload_yaml()  # This will reload the same file you previously loaded
                    else:
                        print("No group selector found, skipping group population.")

            except yaml.YAMLError as e:
                # Handle YAML parsing errors (if the file is malformed)
                QMessageBox.critical(self.window, "YAML Error", f"Error parsing YAML file: {e}")
                print(f"Error parsing YAML file: {e}")

            except Exception as e:
                # Handle any other unexpected errors
                QMessageBox.critical(self.window, "Error", f"An unexpected error occurred: {e}")
                print(f"Error loading YAML: {e}")



def main():
    # Initialize the application
    app = QApplication(sys.argv)
    #app.setStyleSheet("QWidget { background-color: lightblue; }")
    # Create the main window

    window = UI.MainWindow()
    window.setWindowTitle("YAMLConfigManager - ExplodeAny")
    window.setStyleSheet("QMainWindow { background-color: lightgrey; }")
    window.setWindowIcon(QIcon('Icons/service-logo.png'))



    # Create an instance of MainInputOutput to handle input/output logic
    io_handler = MainInputOutput(window)

    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
