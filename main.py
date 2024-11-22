import sys
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QHBoxLayout, QMessageBox, QAbstractItemView,
                               QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
                               QLineEdit, QLabel, QRadioButton, QButtonGroup,
                               QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QMetaObject, Q_ARG
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon

def get_running_path(relative_path):
    if '_internal' in os.listdir():
        return os.path.join('_internal', relative_path)
    else:
        return relative_path

class Worker(QThread):
    # Signals to notify the GUI thread
    update_items_signal = Signal(list)
    finished_signal = Signal()

    def __init__(self, folder_path, filter_in, filter_out, search_type):
        super().__init__()
        self.folder_path = folder_path
        self.filter_in = filter_in
        self.filter_out = filter_out
        self.search_type = search_type
        self.cached_items = []

    def run(self):
        items = self.get_items(self.folder_path)
        self.update_items_signal.emit(items)  # Emit signal to update GUI with the items
        self.finished_signal.emit()

    def get_items(self, folder):
        item_list = []
        for root, dirs, files in os.walk(folder):
            if self.search_type in ["Folders", "Both"]:
                for folder_name in dirs:
                    if self.filter_in in folder_name.lower() and (not self.filter_out or self.filter_out not in folder_name.lower()):
                        folder_path = os.path.join(root, folder_name)
                        creation_time = os.path.getctime(folder_path)
                        size = 0
                        item_list.append({"name": folder_name, "path": folder_path, "creation_time": creation_time, "size": size})
            if self.search_type in ["Files", "Both"]:
                for file_name in files:
                    if self.filter_in in file_name.lower() and (not self.filter_out or self.filter_out not in file_name.lower()):
                        file_path = os.path.join(root, file_name)
                        creation_time = os.path.getctime(file_path)
                        size = os.path.getsize(file_path)
                        item_list.append({"name": file_name, "path": file_path, "creation_time": creation_time, "size": size})
        return item_list


class FileManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyGUIsearch")
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon(get_running_path('icon.ico')))

        # GUI components
        self.folder_path = ""
        self.filter_in = ""
        self.filter_out = ""
        self.search_type = "Files"

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Select Folder Button
        self.select_folder_button = QPushButton("Select Folder", self)
        self.select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_folder_button)

        # Filter Inputs
        self.filter_in_label = QLabel("Filter IN items containing:")
        self.filter_in_entry = QLineEdit(self)
        self.filter_out_label = QLabel("Filter OUT items containing:")
        self.filter_out_entry = QLineEdit(self)

        layout.addWidget(self.filter_in_label)
        layout.addWidget(self.filter_in_entry)
        layout.addWidget(self.filter_out_label)
        layout.addWidget(self.filter_out_entry)

        # Search Type Radio Buttons
        self.files_radio = QRadioButton("Files", self)
        self.folders_radio = QRadioButton("Folders", self)
        self.both_radio = QRadioButton("Both", self)

        self.files_radio.setChecked(True)

        radio_group = QButtonGroup(self)
        radio_group.addButton(self.files_radio)
        radio_group.addButton(self.folders_radio)
        radio_group.addButton(self.both_radio)

        layout.addWidget(self.files_radio)
        layout.addWidget(self.folders_radio)
        layout.addWidget(self.both_radio)

        # Search Button
        self.search_files_button = QPushButton("Search", self)
        self.search_files_button.clicked.connect(self.search_files)

        # copy/ move/ delete buttons layout
        button_layout = QHBoxLayout()

        # Add buttons to the horizontal layout
        self.copy_button = QPushButton("Copy", self)
        self.copy_button.clicked.connect(self.copy_items)
        button_layout.addWidget(self.copy_button)

        self.move_button = QPushButton("Move", self)
        self.move_button.clicked.connect(self.move_items)
        button_layout.addWidget(self.move_button)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_items)
        button_layout.addWidget(self.delete_button)

        # Add the horizontal layout to the main vertical layout
        layout.addWidget(self.search_files_button)
        layout.addLayout(button_layout)  # This adds the buttons on the same line

        # Table to display results
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "File Path", "Creation Date", "File Size (MB)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Make rows read-only
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set the selection mode to select entire rows
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # set alternating rows colors
        self.table.setAlternatingRowColors(True)

        # Set a custom color for the selected rows using CSS
        self.table.setStyleSheet("QTableView::item:selected{"
                                 "background:rgb(135, 206, 255)}")

        # enable sorting in the main table when clicking on the column names
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def copy_items(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            print("No item selected.")
            return

        # Ask for the destination folder
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_folder:
            return

        for row in selected_rows:
            item_path = self.table.item(row.row(), 1).text()  # Get the file/folder path
            dest_path = os.path.join(dest_folder, os.path.basename(item_path))  # Destination path
            if os.path.isdir(item_path):
                shutil.copytree(item_path, dest_path)  # Copy folder
            else:
                shutil.copy2(item_path, dest_path)  # Copy file

        print(f"Items copied to {dest_folder}")

    def move_items(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            print("No item selected.")
            return

        # Ask for the destination folder
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_folder:
            return

        for row in selected_rows:
            item_path = self.table.item(row.row(), 1).text()  # Get the file/folder path
            dest_path = os.path.join(dest_folder, os.path.basename(item_path))  # Destination path
            if os.path.isdir(item_path):
                shutil.move(item_path, dest_path)  # Move folder
            else:
                shutil.move(item_path, dest_path)  # Move file

        print(f"Items moved to {dest_folder}")

    def delete_items(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            print("No item selected.")
            return

        # Confirm before deletion
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete the selected items?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        for row in selected_rows:
            item_path = self.table.item(row.row(), 1).text()  # Get the file/folder path
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete folder
            else:
                os.remove(item_path)  # Delete file

        print("Items deleted.")

    def select_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self)
        if folder_selected:
            self.folder_path = folder_selected
            self.setWindowTitle(f'pyGUIsearch: {self.folder_path}')

    def search_files(self):
        self.filter_in = self.filter_in_entry.text().strip().lower()
        self.filter_out = self.filter_out_entry.text().strip().lower()
        self.search_type = "Files" if self.files_radio.isChecked() else "Folders" if self.folders_radio.isChecked() else "Both"

        if not self.folder_path:
            print("Please specify a folder.")
            return

        # Disable UI during search
        self.select_folder_button.setEnabled(False)
        self.search_files_button.setEnabled(False)

        # Start the worker thread
        self.worker = Worker(self.folder_path, self.filter_in, self.filter_out, self.search_type)
        self.worker.update_items_signal.connect(self.update_table)
        self.worker.finished_signal.connect(self.search_finished)
        self.worker.start()

    def update_table(self, items):
        self.table.setRowCount(0)  # Clear previous results
        for item in items:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row_position, 1, QTableWidgetItem(item['path']))
            self.table.setItem(row_position, 2, QTableWidgetItem(datetime.fromtimestamp(item['creation_time']).strftime('%Y-%m-%d %H:%M:%S')))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(round(item['size'] / (1024 * 1024), 2))))  # Size in MB

    def search_finished(self):
        # Enable the UI after the search is finished
        self.select_folder_button.setEnabled(True)
        self.search_files_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManagerApp()
    window.show()
    sys.exit(app.exec())
