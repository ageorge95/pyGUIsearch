import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime
from tkinter import ttk
from tkinter import PhotoImage


class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pyGUIsearch")
        self.root.geometry("1200x600")

        self.folder_path = ""
        self.filter_in_containing = ""
        self.filter_out_containing = ""
        self.search_type = "Files"  # Default search type is files
        self.sort_column = "Creation Date"  # Default sorting column
        self.sort_reverse = False  # Sorting direction

        # Load icons for sorting from image files
        self.up_arrow = PhotoImage(file="up_arrow.png")  # Ensure the file exists
        self.down_arrow = PhotoImage(file="down_arrow.png")  # Ensure the file exists

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        self.search_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.search_button.pack(pady=10)

        # Create a frame to hold the filter in filter
        self.search_filter_in_frame = tk.Frame(self.root)
        self.search_filter_in_frame.pack(pady=5)

        # Add the labels and entries for filter in filter
        self.filter_in_label = tk.Label(self.search_filter_in_frame, text="Filter IN items containing (e.g. .txt, .rrec):")
        self.filter_in_label.pack(side=tk.LEFT, padx=5)

        self.filter_in_entry = tk.Entry(self.search_filter_in_frame)
        self.filter_in_entry.pack(side=tk.LEFT, padx=5)

        # Create a frame to hold the filter out filter
        self.search_filter_out_frame = tk.Frame(self.root)
        self.search_filter_out_frame.pack(pady=5)

        self.filter_out_label = tk.Label(self.search_filter_out_frame, text="Filter OUT items containing (e.g. .txt, .rrec):")
        self.filter_out_label.pack(side=tk.LEFT, padx=5)

        self.filter_out_entry = tk.Entry(self.search_filter_out_frame)
        self.filter_out_entry.pack(side=tk.LEFT, padx=5)

        # Radio buttons for selecting search type (Files, Folders, or Both)
        self.search_type_var = tk.StringVar(value="Files")

        # Create a frame to hold the radio buttons
        self.radio_frame = tk.Frame(self.root)
        self.radio_frame.pack(pady=5)

        # Add the radio buttons to the frame
        self.files_radio = tk.Radiobutton(self.radio_frame, text="Files", variable=self.search_type_var, value="Files")
        self.files_radio.pack(side=tk.LEFT, padx=5)

        self.folders_radio = tk.Radiobutton(self.radio_frame, text="Folders", variable=self.search_type_var,
                                            value="Folders")
        self.folders_radio.pack(side=tk.LEFT, padx=5)

        self.both_radio = tk.Radiobutton(self.radio_frame, text="Both", variable=self.search_type_var, value="Both")
        self.both_radio.pack(side=tk.LEFT, padx=5)

        self.search_files_button = tk.Button(self.root, text="Search", command=self.search_files)
        self.search_files_button.pack(pady=10)

        # Treeview to display files with scrollbars
        self.treeview_frame = tk.Frame(self.root)
        self.treeview_frame.pack(fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(self.treeview_frame, columns=("Name", "Path", "Creation Date", "Size"),
                                     show="headings")
        self.treeview.heading("Name", text="File Name", command=lambda: self.sort_column_click("Name"))
        self.treeview.heading("Path", text="File Path", command=lambda: self.sort_column_click("Path"))
        self.treeview.heading("Creation Date", text="Creation Date",
                              command=lambda: self.sort_column_click("Creation Date"))
        self.treeview.heading("Size", text="File Size (MB)", command=lambda: self.sort_column_click("Size"))
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertical scrollbar for treeview
        self.treeview_scroll_y = ttk.Scrollbar(self.treeview_frame, orient="vertical", command=self.treeview.yview)
        self.treeview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.treeview_scroll_y.set)

        # Create a frame to hold the buttons
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=5)

        # Add the buttons to the frame
        self.move_button = tk.Button(self.buttons_frame, text="Move Files", command=self.move_files)
        self.move_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = tk.Button(self.buttons_frame, text="Copy Files", command=self.copy_files)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.buttons_frame, text="Delete Files", command=self.delete_files)
        self.delete_button.pack(side=tk.LEFT, padx=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            messagebox.showinfo("Folder Selected", f"Selected folder: {self.folder_path}")
            self.root.title('pyGUIsearch: ' + self.folder_path)

    def search_files(self):
        self.filter_in_containing = self.filter_in_entry.get().strip()
        self.filter_out_containing = self.filter_out_entry.get().strip()
        self.search_type = self.search_type_var.get()

        if not self.folder_path:
            messagebox.showwarning("Input Error", "Please specify a folder.")
            return

        self.treeview.delete(*self.treeview.get_children())  # Clear previous results
        items = self.get_items(self.folder_path)

        # Sort items based on the selected column and order
        if self.sort_column == "Creation Date":
            items = sorted(items, key=lambda x: x['creation_time'], reverse=self.sort_reverse)
        elif self.sort_column == "Name":
            items = sorted(items, key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Path":
            items = sorted(items, key=lambda x: x['path'].lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Size":
            items = sorted(items, key=lambda x: x['size'], reverse=self.sort_reverse)

        for item in items:
            creation_time = datetime.fromtimestamp(item['creation_time']).strftime('%Y-%m-%d %H:%M:%S')
            size_mb = round(item['size'] / (1024 * 1024), 2)  # Convert size to MB and round it
            self.treeview.insert("", "end", values=(item['name'], item['path'], creation_time, size_mb))

        self.update_column_icons()

    def get_items(self, folder):
        item_list = []
        for root, dirs, files in os.walk(folder):
            # Add folders to the list if "Folders" or "Both" is selected
            if self.search_type in ["Folders", "Both"]:
                for folder_name in dirs:
                    if (self.filter_in_containing in folder_name.lower() and
                            (not self.filter_out_containing or
                             (self.filter_out_containing and self.filter_out_containing not in folder_name.lower()))):
                        folder_path = os.path.join(root, folder_name)
                        creation_time = os.path.getctime(folder_path)
                        size = 0  # Folders usually don't have size, set it to 0
                        item_list.append({
                                             "name": folder_name,
                                             "path": folder_path,
                                             "creation_time": creation_time,
                                             "size": size
                                         })

            # Add files to the list if "Files" or "Both" is selected
            if self.search_type in ["Files", "Both"]:
                for file_name in files:
                    if (self.filter_in_containing in file_name.lower() and
                            (not self.filter_out_containing or
                             (self.filter_out_containing and self.filter_out_containing not in file_name.lower()))):
                        file_path = os.path.join(root, file_name)
                        creation_time = os.path.getctime(file_path)
                        size = os.path.getsize(file_path)  # Get file size in bytes
                        item_list.append({
                                             "name": file_name,
                                             "path": file_path,
                                             "creation_time": creation_time,
                                             "size": size
                                         })

        return item_list

    def sort_column_click(self, column):
        # Toggle the sorting direction if the same column is clicked again
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False  # Default to ascending for new columns

        self.search_files()  # Refresh the file list with new sorting order

    def update_column_icons(self):
        """Update column icons based on the sorted column and direction."""
        for col in ["Name", "Path", "Creation Date", "Size"]:
            self.treeview.heading(col, text=col)  # Reset the text of all columns

        if self.sort_column == "Name":
            icon = self.up_arrow if not self.sort_reverse else self.down_arrow
            self.treeview.heading("Name", text="File Name", image=icon)
        elif self.sort_column == "Path":
            icon = self.up_arrow if not self.sort_reverse else self.down_arrow
            self.treeview.heading("Path", text="File Path", image=icon)
        elif self.sort_column == "Creation Date":
            icon = self.up_arrow if not self.sort_reverse else self.down_arrow
            self.treeview.heading("Creation Date", text="Creation Date", image=icon)
        elif self.sort_column == "Size":
            icon = self.up_arrow if not self.sort_reverse else self.down_arrow
            self.treeview.heading("Size", text="File Size (MB)", image=icon)

        # Keep the icons from being stretched out
        self.treeview.heading("Name", anchor="w")
        self.treeview.heading("Path", anchor="w")
        self.treeview.heading("Creation Date", anchor="w")
        self.treeview.heading("Size", anchor="w")

    def move_files(self):
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select items to move.")
            return

        destination = filedialog.askdirectory()
        if not destination:
            return

        for item in selected_items:
            file_path = self.treeview.item(item, "values")[1]
            try:
                if os.path.isfile(file_path):
                    shutil.move(file_path, destination)
                elif os.path.isdir(file_path):
                    shutil.move(file_path, os.path.join(destination, os.path.basename(file_path)))
            except Exception as e:
                messagebox.showerror("Error", f"Error moving item {file_path}: {e}")
                continue
        messagebox.showinfo("Success", "Items moved successfully.")
        self.search_files()  # Refresh the file list

    def copy_files(self):
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select items to copy.")
            return

        destination = filedialog.askdirectory()
        if not destination:
            return

        for item in selected_items:
            file_path = self.treeview.item(item, "values")[1]
            try:
                if os.path.isfile(file_path):
                    shutil.copy(file_path, destination)
                elif os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(destination, os.path.basename(file_path)))
            except Exception as e:
                messagebox.showerror("Error", f"Error copying item {file_path}: {e}")
                continue
        messagebox.showinfo("Success", "Items copied successfully.")
        self.search_files()  # Refresh the file list

    def delete_files(self):
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select items to delete.")
            return

        confirmation = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected items?")
        if not confirmation:
            return

        for item in selected_items:
            file_path = self.treeview.item(item, "values")[1]
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting item {file_path}: {e}")
                continue
        messagebox.showinfo("Success", "Items deleted successfully.")
        self.search_files()  # Refresh the file list


# Main Application
root = tk.Tk()
app = FileManagerApp(root)
root.mainloop()
