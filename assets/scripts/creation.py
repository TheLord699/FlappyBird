import tkinter.messagebox as messagebox
import tkinter as tk
import shutil
import os
import re

from tkinter import filedialog
from pathlib import Path

class CharacterCreator:
    def __init__(self, flappy_bird: 'FlappyBird') -> None: # type: ignore
        self.flappy_bird: 'FlappyBird' = flappy_bird # type: ignore
        self.imported_files: dict[str, list[str]] = {}

    def update(self) -> None:
        if self.flappy_bird.menu == "creator":
            self.show_import_rules()
            self.select_import()

        if self.flappy_bird.menu == "delete":
            self.select_delete()

    def show_import_rules(self) -> None:
        import_text = (
            "Welcome to the Character Creator!\n\n"
            "Please follow these rules when importing files:\n"
            "- Files should be image files PNG only.\n"
            "- All files must have the same name to be put in the same folder\n"
            "- Files must be put in at the same time to go into the same folder\n"
            "- Each file should represent a different skin for the character.\n"
            "- File names should start with the name of the skin, followed by numbers (e.g., skin1.png, skin2.png).\n\n"
            "After selecting files, they will be copied to the appropriate folders in the 'assets/sprites/player' directory.\n"
            "If a folder with the same name already exists, it will not be overwritten, and you'll be prompted to choose another name.\n"
            "You can import multiple files at once by highlighting multiple files, doing this with files of the same name will put them\n"
            "all in the same folder."
        )
        messagebox.showinfo("Character Creator Rules", import_text)

    def show_deletion_rules(self) -> None:
        deletion_text = "Select a file or files to delete"
        messagebox.showinfo("Deletion Info", deletion_text)

    def select_import(self) -> None:
        self.imported_files = {}
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames()
        if not file_paths:
            self.flappy_bird.menu = "main"
            return

        if len(file_paths) == 1:
            file_path = file_paths[0]
            if not file_path.lower().endswith('.png'):
                messagebox.showerror("Error", f"File '{file_path}' is not a PNG file. Only PNG files are allowed.")
                self.flappy_bird.menu = "main"
                return

            file_name = os.path.splitext(os.path.basename(file_path))[0]
            new_file_name = re.sub(r'\d+', '', file_name) + '.png'
            folder_name = new_file_name.split('.')[0]

            self.imported_files[folder_name] = [file_path]

            self.destination_folder = os.path.join("assets", "sprites", "player", folder_name)
            if not os.path.exists(self.destination_folder):
                os.makedirs(self.destination_folder)
                
            else:
                messagebox.showerror("Error", f"Folder '{folder_name}' already exists. Please choose another name.")
                self.flappy_bird.menu = "main"
                return

            destination_path = os.path.join(self.destination_folder, new_file_name)
            shutil.copy(file_path, destination_path)
            
        else:
            for file_path in file_paths:
                if not file_path.lower().endswith('.png'):
                    messagebox.showerror("Error", f"File '{file_path}' is not a PNG file. Only PNG files are allowed.")
                    self.imported_files.clear()
                    return

                file_name = os.path.splitext(os.path.basename(file_path))[0]
                folder_name = re.sub(r'\d+', '', file_name)
                if folder_name not in self.imported_files:
                    self.imported_files[folder_name] = []

                self.imported_files[folder_name].append(file_path)

            for folder_name, files in self.imported_files.items():
                base_name = re.sub(r'\d+', '', os.path.splitext(os.path.basename(files[0]))[0])
                numbers = []
                for file in files:
                    if re.sub(r'\d+', '', os.path.splitext(os.path.basename(file))[0]) != base_name:
                        messagebox.showerror(
                            "Error",
                            f"Files in folder '{folder_name}' do not have the same base name. Please ensure all files start with '{base_name}'."
                        )
                        self.imported_files.clear()
                        return
                    
                    number = int(re.search(r'\d+', os.path.splitext(os.path.basename(file))[0]).group())
                    numbers.append(number)

                numbers.sort()
                expected_numbers = list(range(1, len(numbers) + 1))
                if numbers != expected_numbers:
                    messagebox.showerror(
                        "Error",
                        f"Files in folder '{folder_name}' have missing numbers. The sequence should be continuous without gaps."
                    )
                    self.imported_files.clear()
                    return

                self.destination_folder = os.path.join("assets", "sprites", "player", folder_name)
                if not os.path.exists(self.destination_folder):
                    os.makedirs(self.destination_folder)
                    
                else:
                    messagebox.showerror("Error", f"Folder '{folder_name}' already exists. Please choose another name.")
                    self.imported_files.clear()
                    return

                for file in files:
                    destination_path = os.path.join(self.destination_folder, os.path.basename(file))
                    shutil.copy(file, destination_path)

        if len(self.imported_files) == 1:
            self.choose_sprite_type()
            
        self.flappy_bird.skins = [folder.name for folder in Path("assets/sprites/player").iterdir() if folder.is_dir()]
        self.flappy_bird.menu = "main"

    def choose_sprite_type(self) -> None:
        with open("assets/sprites/player/data_stationary.txt", "a") as file:
            for folder_name in self.imported_files.keys():
                choice = messagebox.askyesno(
                    "Sprite Type",
                    f"Do you want the sprites in folder '{folder_name}' to be stationary? (If not, they will rotate)"
                )
                if choice:
                    file.write(folder_name + "\n")
                    
                else:
                    with open("assets/sprites/player/data_stationary.txt", "r") as f:
                        lines = f.readlines()

                    with open("assets/sprites/player/data_stationary.txt", "w") as f:
                        for line in lines:
                            if line.strip("\n") != folder_name:
                                f.write(line)

    def select_delete(self) -> None:
        self.show_deletion_rules()
        root = tk.Tk()
        root.withdraw()
        
        file_paths = filedialog.askopenfilenames(initialdir="assets/sprites/player")
        if not file_paths:
            self.flappy_bird.menu = "main"
            return

        for file_path in file_paths:
            abs_file_path = os.path.abspath(file_path)
            base_dir = os.path.abspath("assets/sprites/player")
            if not abs_file_path.startswith(base_dir):
                messagebox.showerror(
                    "Error",
                    f"File '{file_path}' is not in the 'assets/sprites/player' directory or its subdirectories. "
                    "Only files or folders from this directory can be deleted."
                )
                continue

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file_path}'?")
            if not confirm:
                continue

            if os.path.isfile(file_path) and file_path.lower().endswith('.png'):
                folder_path = os.path.dirname(file_path)
                if self.deletion_breaks_sequence(folder_path, file_path):
                    messagebox.showerror(
                        "Error",
                        f"Deleting '{file_path}' would break the sequence. Please ensure the sequence remains continuous without gaps."
                    )
                    continue

                os.remove(file_path)
                messagebox.showinfo("File Deleted", f"File '{file_path}' has been deleted.")
                
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                messagebox.showinfo("Folder Deleted", f"Folder '{file_path}' has been deleted.")
                
            else:
                messagebox.showwarning("Warning", f"File '{file_path}' is not a PNG file and won't be deleted.")

            self.rename_file_if_necessary(os.path.dirname(file_path))

        self.flappy_bird.skins = [folder.name for folder in Path("assets/sprites/player").iterdir() if folder.is_dir()]
        self.flappy_bird.menu = "main"

    def deletion_breaks_sequence(self, folder_path: str, file_to_delete: str) -> bool:
        file_to_delete_name = os.path.basename(file_to_delete)
        match = re.search(r'(\D+)(\d+)\.png$', file_to_delete_name)
        if not match:
            return False

        base_name, number_to_delete = match.groups()
        number_to_delete = int(number_to_delete)

        files_in_folder = [f for f in os.listdir(folder_path) if re.match(rf'{base_name}\d+\.png$', f)]
        numbers = sorted([int(re.search(r'(\d+)\.png$', f).group(1)) for f in files_in_folder])

        if numbers == list(range(1, len(numbers) + 1)):
            numbers.remove(number_to_delete)
            if numbers == list(range(1, len(numbers) + 1)):
                return False

        return True

    def rename_file_if_necessary(self, folder_path: str) -> None:
        files = os.listdir(folder_path)
        numbers = [int(re.search(r'(\d+)\.png$', f).group(1)) for f in files if re.search(r'(\d+)\.png$', f)]
        if len(numbers) > 0 and max(numbers) > 1:
            return

        for file in files:
            file_path = os.path.join(folder_path, file)
            file_name, file_ext = os.path.splitext(file)
            if file_ext.lower() == '.png' and re.search(r'1$', file_name):
                new_file_name = re.sub(r'1$', '', file_name) + file_ext
                new_file_path = os.path.join(folder_path, new_file_name)
                
                os.rename(file_path, new_file_path)
                messagebox.showinfo("File Renamed", f"File '{file}' has been renamed to '{new_file_name}'")
