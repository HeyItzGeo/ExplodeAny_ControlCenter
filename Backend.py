import yaml
import os


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
        """
        if not self.file_path:
            raise ValueError(
                "No configuration file loaded. Please load a config first."
            )

        try:
            with open(self.file_path, "w") as file:
                yaml.safe_dump(self.config_data, file)
        except Exception as e:
            print(f"Error saving config: {e}")
            raise

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


class YAMLConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.yaml_data = None
            cls._instance.file_path = None
        return cls._instance

    def load_yaml(self, file_path):
        """
        Loads the YAML file into memory and parses it.
        """

        try:
            with open(file_path, "r") as file:
                self.yaml_data = yaml.safe_load(file)
            self.file_path = file_path
            print(f"YAML loaded from {file_path}")
            self.parse_yaml()
        except Exception as e:
            print(f"Error loading YAML file: {e}")

    def parse_yaml(self):
        """
        Parses and organizes the YAML data for easy access.
        """
        if self.yaml_data is None:
            print("No data loaded to parse.")
            return

        # print(f"Groups: {self.yaml_data.get('Groups')}")

    def get_yaml_data(self):
        """
        Returns the current YAML data in memory.
        """
        return self.yaml_data

    def get_file_path(self):
        """
        Returns the file path of the currently loaded YAML file.
        """
        return os.path.abspath(self.file_path)

    def get_value(self, path, default=None):
        """
        Dynamically access a value by providing a path (e.g., 'Groups.aa').
        Supports nested keys in YAML (dot notation).

        If the key is not found, returns the specified default value (or None if not specified).
        """
        keys = path.split(".")
        value = self.yaml_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:

                print(
                    f"Key '{key}' not found in the current structure. Returning default value."
                )
                return default

        return value

    def add_values(self, path, new_entries):
        """
        Adds multiple key-value pairs to a specific path in the YAML structure
        and writes the updated YAML back to the file.

        new_entries: A dictionary of new key-value pairs to add.
        """
        keys = path.split(".")
        value = self.yaml_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                print(f"Key '{key}' not found in the current structure.")
                return False

        if isinstance(value, dict):

            value.update(new_entries)

            self._write_yaml_file()

            return True
        else:
            print(
                f"Cannot add values. The final key '{keys[-1]}' should be a dictionary."
            )
            return False

    def _write_yaml_file(self):
        """
        Writes the updated YAML data to the file.
        """
        if self.file_path:
            try:
                with open(self.file_path, "w") as file:
                    yaml.dump(self.yaml_data, file, default_flow_style=False)
                    print(f"YAML file updated and saved to {self.file_path}")
            except Exception as e:
                print(f"Error writing YAML file: {e}")
        else:
            print("No file path specified to write the YAML data.")

    def set_value(self, path, new_value):
        """
        Dynamically set a value by providing a path (e.g., 'Groups.aa')
        and the new value.
        """
        keys = path.split(".")
        value = self.yaml_data

        for key in keys[:-1]:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                print(f"Key '{key}' not found in the current structure.")
                return False

        final_key = keys[-1]
        if isinstance(value, dict):
            value[final_key] = new_value
            return True
        else:
            print(
                f"Cannot set value. The last part of the path should be a dictionary."
            )
            return False



    def remove_item_from_group(self, group_name, item):
        """
        Removes a specific item from a group in the 'Groups' section.

        Args:
            group_name (str): The name of the group to remove the item from.
            item (str): The item to remove from the group.
        """
        if self.yaml_data and "Groups" in self.yaml_data:
            groups = self.yaml_data["Groups"]

            if group_name in groups:
                group_items = groups[group_name]
                
                if isinstance(group_items, list):
                    if item in group_items:
                        group_items.remove(item)
                        print(f"Item '{item}' removed from group '{group_name}'.")

                        # If the list is empty, convert it to an empty dictionary
                        if not group_items:
                            groups[group_name] = {}
                            print(f"Group '{group_name}' is now an empty dictionary.")
                        
                        self._write_yaml_file()
                        return True
                    else:
                        print(f"Item '{item}' not found in group '{group_name}'.")
                        return False
                else:
                    print(f"Group '{group_name}' is not a list. Cannot remove item.")
                    return False
            else:
                print(f"Group '{group_name}' does not exist.")
                return False
        else:
            print("No 'Groups' section found in YAML data.")
            return False


    def add_items_to_group(self, group_name, items):
        if self.yaml_data and "Groups" in self.yaml_data:
            groups = self.yaml_data["Groups"]

            if group_name in groups:
                existing_items = groups[group_name]

                if isinstance(existing_items, list):
                    # If the group is already a list, add items directly, even if they are the same
                    for item in items:
                        existing_items.append(item)  # Just append without checking for duplicates
                elif isinstance(existing_items, dict):
                    # If the group is a dictionary, convert it to a list and add items
                    print(f"Group '{group_name}' is a dictionary. Converting it to a list and adding items.")
                    groups[group_name] = []  # Convert dictionary to an empty list

                    # Append the items, even if they are the same as others
                    for item in items:
                        groups[group_name].append(item)

                else:
                    print(
                        f"Group '{group_name}' exists, but it is not a list or dictionary. It is a {type(existing_items)}."
                    )
                    return False

                # After adding items, write to the YAML file
                self._write_yaml_file()
                print(f"Items {items} added to group '{group_name}'.")
                return True
            else:
                print(f"Group '{group_name}' does not exist. No items were added.")
                return False
        else:
            print("No 'Groups' structure found in the YAML data.")
            return False




    def set_nested_value(
        self, entity_group_name, group_name, section, property_name, new_value
    ):
        """
        Set a property value inside a specified section ('Properties' or 'Materials').

        Args:
        - entity_group_name (str): The entity group name (e.g., 'EntityGroup3').
        - group_name (str): The block or entity group name (e.g., 'BlockGroup3') for 'Materials'. Pass None for 'Properties'.
        - section (str): The section name ('Properties' or 'Materials').
        - property_name (str): The property name to update (e.g., 'Damage' or 'ExplosionRemoveNearbyLiquids').
        - new_value: The new value to set for the property.

        Returns:
        - bool: True if the value was updated successfully, False otherwise.
        """
        try:
            if section == "Properties":

                path = f"VanillaEntity.{entity_group_name}.{section}.{property_name}"
            elif section == "Materials":

                if not group_name:
                    print("group_name must be specified for Materials.")
                    return False
                path = f"VanillaEntity.{entity_group_name}.{section}.{group_name}.{property_name}"
            else:
                print(
                    f"Invalid section: {section}. Only 'Properties' or 'Materials' allowed."
                )
                return False

            if self.set_value(path, new_value):
                print(f"Updated {path} to {new_value}.")
                self._write_yaml_file()
                return True
            else:
                print(
                    f"Failed to update {path}. Key might not exist in the YAML structure."
                )
                return False
        except Exception as e:
            print(f"Error in set_nested_value: {e}")
            return False


def retrieve_group_items(config_manager, group_name):
    """Retrieve and return items for a specific group."""
    group_items = config_manager.get_value(f"Groups.{group_name}")

    if group_items is not None:
        print(f"Items in {group_name}: {group_items}")
        return group_items
    else:
        print(f"Group '{group_name}' not found.")
        return {}


def get_parent_key(self, section_path):
    """
    Retrieve the immediate parent key of the specified section path.
    For example, if section_path is "VanillaEntity.Apple.Properties",
    it will return "Apple".
    """
    keys = section_path.split(".")
    if len(keys) > 1:
        return keys[-2]
    return None


def Add_Group_Pairs(
    config_manager,
    EntityGroupName,
    BlockGroupName,
    entity_particles_checked,
    block_particles_checked,
    entity_sounds_checked,
    block_sounds_checked,
):

    new_entries = {"Groups": {f"{EntityGroupName}": {}, f"{BlockGroupName}": {}}}

    config_manager.add_values("Groups", new_entries["Groups"])

    vanilla_entity_entries = {
        "VanillaEntity": {
            f"{EntityGroupName}": {
                "Materials": {
                    f"{BlockGroupName}": _generate_materials(
                        block_particles_checked, block_sounds_checked
                    )
                },
                "Properties": _generate_properties(
                    entity_particles_checked, entity_sounds_checked
                ),
            }
        }
    }

    config_manager.add_values("VanillaEntity", vanilla_entity_entries["VanillaEntity"])

    Output_Groups = config_manager.get_value("Groups")
    Output_VanillaEntity = config_manager.get_value("VanillaEntity")


def _generate_properties(entity_particles_checked, entity_sounds_checked):
    properties = {
        "ExplosionRadius": 0.0,
        "ExplosionFactor": 1.0,
        "ReplaceOriginalExplosion": False,
        "UnderwaterExplosionFactor": 0.5,
        "ExplosionDamageBlocksUnderwater": False,
        "ReplaceOriginalExplosionWhenUnderwater": True,
        "ExplosionRemoveWaterloggedStateFromNearbyBlocks": False,
        "ExplosionRemoveWaterloggedStateFromNearbyBlocksOnSurface": True,
        "ExplosionRemoveWaterloggedStateFromNearbyBlocksUnderwater": True,
        "ExplosionRemoveNearbyWaterloggedBlocks": False,
        "ExplosionRemoveNearbyWaterloggedBlocksOnSurface": True,
        "ExplosionRemoveNearbyWaterloggedBlocksUnderwater": True,
        "ExplosionRemoveNearbyLiquids": False,
        "ExplosionRemoveNearbyLiquidsOnSurface": True,
        "ExplosionRemoveNearbyLiquidsUnderwater": True,
        "PackDroppedItems": False,
    }

    if entity_particles_checked:
        properties["Particles"] = {
            "Name": "REDSTONE",
            "DeltaX": 2.0,
            "DeltaY": 2.0,
            "DeltaZ": 2.0,
            "Amount": 2000,
            "Speed": 1.0,
            "Force": True,
            "Red": 255,
            "Green": 0,
            "Blue": 255,
            "Size": 2.0,
        }

    if entity_sounds_checked:
        properties["Sound"] = {
            "Name": "ENTITY_OCELOT_HURT",
            "Volume": 1.0,
            "Pitch": 1.0,
        }

    return properties


def _generate_materials(block_particles_checked, block_sounds_checked):
    materials = {
        "Damage": 50.0,
        "DropChance": 0.0,
        "DistanceAttenuationFactor": 0.0,
        "UnderwaterDamageFactor": 0.5,
        "FancyUnderwaterDetection": False,
    }

    if block_particles_checked:
        materials["Particles"] = {
            "DeltaX": 5.0,
            "DeltaY": 5.0,
            "DeltaZ": 5.0,
            "Amount": 2000,
            "Speed": 1.0,
            "Force": True,
            "Name": "BLOCK_CRACK",
            "Material": "OBSIDIAN",
        }

    if block_sounds_checked:
        materials["Sound"] = {"Name": "ENTITY_OCELOT_HURT", "Volume": 1.0, "Pitch": 1.0}

    return materials


def test_yaml_manager():

    config_manager = YAMLConfigManager()

    test_file_path = "test_config.yaml"

    config_manager.load_yaml(test_file_path)

    EntityGroupName = "EntityGroup1"
    BlockGroupName = "BlockGroup1"
    Add_Group_Pairs(config_manager, EntityGroupName, BlockGroupName)

    new_value = 100.0
    property_name = "ExplosionRadius"
    section = "Properties"
    group_name = None
    result = config_manager.set_nested_value(
        EntityGroupName, BlockGroupName, section, property_name, new_value
    )

    print(f"Update Result: {result}")
    print(
        f"Updated value for {property_name}: {config_manager.get_value(f'VanillaEntity.{EntityGroupName}.{section}.{property_name}')}"
    )

    material_property_name = "Damage"
    material_new_value = 75.0
    result = config_manager.set_nested_value(
        EntityGroupName,
        BlockGroupName,
        "Materials",
        material_property_name,
        material_new_value,
    )

    print(
        f"Updated value for {material_property_name}: {config_manager.get_value(f'VanillaEntity.{EntityGroupName}.Materials.{BlockGroupName}.{material_property_name}')}"
    )

    group_name = "Group1"
    items = ["stone", "dirt", "grass"]
    config_manager.add_items_to_group(group_name, items)


if __name__ == "__main__":
    test_yaml_manager()
