# ExplodeAny ControlCenter for Minecraft

Welcome to the **ExplodeAny** configuration editor! This tool is designed to help you easily configure the **ExplodeAny** plugin for Minecraft.

## 📦 Installation
To use the **ExplodeAny ControlCenter**, you'll need to download and install the **ExplodeAny** plugin from the repository. Follow the installation instructions provided in the plugin's GitHub repository.

## 🔗 Check it Out!
Discover the full capabilities of the **ExplodeAny** plugin on GitHub:

[Explore the GitHub repository here!](https://github.com/GuilleX7/ExplodeAny/tree/main)

---
## 🚀 Download & Run

- **For Windows Users**: You can download the **.exe** version of the **[ExplodeAny ControlCenter](https://github.com/HeyItzGeo/ExplodeAny_ControlCenter/releases/download/V2/ExplodeAny_ControlCenter.exe)** from the release section of the GitHub repository. This version is ready to run on your system without any extra setup.

- **For Developers or Custom Modifications**: If you want to modify the source code or run the program in a different environment, you can download the source code directly from the GitHub repository.

<details>
  <summary>Click to view the pyinstaller command</summary>

```
pyinstaller --noconfirm --onefile --windowed --name "ExplodeAny_ControlCenter" --clean --splash "Logo.webp" --add-data "Backend.py;." --add-data "MainUIv6.py;." --add-data "Right_PropEditor.py;." --add-data "Icons;Icons/" "Run_ConfigEditor.py"
```

```
  **Folder structure of the project:**

  ExplodeAny_ControlCenter/
  ├── Logo.webp
  ├── Backend.py
  ├── MainUIv6.py
  ├── Right_PropEditor.py
  ├── Icons/ (folder containing icon files)
  └── Run_ConfigEditor.py
```
</details>

---

## 🛠️ How to Use the Configuration Editor

The **ExplodeAny ControlCenter** makes it simple to create and modify configuration files for the **ExplodeAny** plugin. Follow these steps to get started:

### 1. **Loading or Creating a New Config**
   - **To create a new config**:  
     Go to `File > Empty Config`, then choose a location to save your new config and give it a name.
   - **To load an existing config**:  
     Go to `File > Load Config`, then choose your config from a saved location.

### 2. **Adding Entity and Block Groups**
   - After creating or loading a config, you need to define groups for entities and blocks.
   - **To add groups**:  
     Enter a name for both **Entity** and **Block Group Names** (in bold), then click the **Add Group(s) to Config** button. The groups will automatically be saved to the config file at the location you selected.

### 3. **Adding Values to Blocks and Entities**
   - **For Blocks**:  
     To add block values, select the block group name in the middle box and enter block types like `GRASS_BLOCK`, `GLASS`, etc.
   - **For Entities**:  
     To add entity values, select the entity group name in the middle box. You can either enter a custom value or pick from the dropdown list of common entities such as `PRIMED_TNT`, `WITHER`, and more.
  - **Comma-separated values are also accepted**:

### 4. **Modifying Property Values**
   - **For Entity Properties**:  
     Select an entity group from the middle box to view and modify its properties on the right side of the window.
   - **For Block Material Properties**:  
     Select a block group from the middle box to view and edit the material properties on the right side.

### 5. **Saving Your Changes**
   - **For Adding Groups**:  
     Any changes made when adding new **Entity** or **Block Groups** are automatically saved to the config file as you create them.
   - **For Editing Property or Material Values**:  
     When modifying entity properties or block materials, you will need to click the **Save** button on the right side of the window to save your changes.

---

Feel free to contribute or open issues if you have any suggestions or need assistance!
