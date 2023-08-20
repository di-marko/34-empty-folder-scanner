# Created by Dima Markélov @2023

import os, sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QProgressBar, QMessageBox, QTableWidget, QTableWidgetItem, QCheckBox, 
    QHeaderView, QMenuBar, QMenu, QMainWindow, QAction, QDialog, QAbstractItemView
)
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt

# This function is used to load the favicon when the application is packaged
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Empty Folder Scanner")
        self.setWindowIcon(QIcon(resource_path("images/favicon-logo.png")))

        central_widget = QWidget(self)
        layout = QVBoxLayout()

        self.folder_label = QLabel('Folder:')
        self.folder_input = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.search_button = QPushButton('Scan')
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat('0%')
        self.progress_bar.setTextVisible(True)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.progress_bar)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["", "Folder", "Location"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Create a header checkbox
        self.header_checkbox = QCheckBox()
        self.header_checkbox.stateChanged.connect(self.toggle_checkboxes)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.viewport().installEventFilter(self)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.on_header_clicked)

        checkbox_widget = QWidget()
        layout_checkbox = QHBoxLayout(checkbox_widget)
        layout_checkbox.addWidget(self.header_checkbox)
        layout_checkbox.setAlignment(Qt.AlignCenter)
        layout_checkbox.setContentsMargins(0, 0, 0, 0)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setCellWidget(0, 0, checkbox_widget)

        layout.addLayout(folder_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_menu()

        self.browse_button.clicked.connect(self.browse_folder)
        self.search_button.clicked.connect(self.search_folder)

        self.show()

    def create_menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)

        edit_menu = QMenu("Edit", self)
        menubar.addMenu(edit_menu)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected_folders)
        edit_menu.addAction(delete_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        menubar.addAction(about_action)

    def show_about(self):
        about_window = QDialog(self)
        about_window.setWindowTitle("About")
        about_window.setFixedSize(300, 200)
        about_window.setWindowFlags(
            about_window.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout()

        description = "A simple and intuitive application to find empty folders on your computer. Choose a folder to scan, and the application will list all the empty folders within it. You can then select and delete the empty folders.\n\nView the source code on GitHub."
        label = QLabel(description, about_window)
        label.setWordWrap(True)
        label.setMaximumWidth(350)
        layout.addWidget(label)

        author_label = QLabel("Author: Dmitri Markélov", about_window)
        layout.addWidget(author_label)

        button_layout = QHBoxLayout()
        github_button = QPushButton("GitHub", about_window)
        github_button.clicked.connect(
            lambda: self.open_link("https://github.com/di-marko")
        )
        github_button.setFocusPolicy(Qt.NoFocus)
        button_layout.addWidget(github_button)

        linkedin_button = QPushButton("LinkedIn", about_window)
        linkedin_button.clicked.connect(
            lambda: self.open_link("https://www.linkedin.com/in/dimamarkelov/")
        )
        linkedin_button.setFocusPolicy(Qt.NoFocus)
        button_layout.addWidget(linkedin_button)

        layout.addLayout(button_layout)
        about_window.setLayout(layout)
        about_window.exec_()

    def open_link(self, link):
        os.system(f'start "" "{link}"')

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def search_folder(self):
        folder = self.folder_input.text()
        if not folder:
            QMessageBox.warning(self, "Warning", "Please select a folder to scan.")
            return

        self.table.setRowCount(0)
        self.progress_bar.setValue(0)

        empty_folders = []
        for dirpath, dirnames, filenames in os.walk(folder):
            if not dirnames and not filenames:
                empty_folders.append(dirpath)

        self.progress_bar.setMaximum(len(empty_folders))
        for i, folder in enumerate(empty_folders):
            checkbox = QCheckBox()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget = QWidget()
            checkbox_widget.setLayout(checkbox_layout)
            self.table.insertRow(i)
            self.table.setCellWidget(i, 0, checkbox_widget)
            self.table.setItem(i, 1, QTableWidgetItem(os.path.basename(folder)))
            self.table.setItem(i, 2, QTableWidgetItem(folder))
            self.progress_bar.setValue(i + 1)
            self.progress_bar.setFormat(f'{int(100 * (i + 1) / len(empty_folders))}%')
            QApplication.processEvents()

        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

    def contextMenuEvent(self, event):
        item = self.table.itemAt(event.pos())
        if item:
            context_menu = QMenu(self)
            open_action = QAction("Open Folder Location", self)
            open_action.triggered.connect(self.open_folder_location)
            context_menu.addAction(open_action)
            context_menu.exec_(event.globalPos())
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.viewport().installEventFilter(self)
    

    def open_folder_location(self):
        selected_indexes = self.table.selectionModel().selectedIndexes()
        if selected_indexes:
            folder_path = self.table.item(selected_indexes[0].row(), 2).text()
            if os.path.exists(folder_path):
                os.system(f'explorer "{folder_path}"')
            else:
                QMessageBox.warning(self, "Warning", "The folder no longer exists.")
    

    def delete_selected_folders(self):
        selected_rows = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                selected_rows.append(i)
        
        if not selected_rows:
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to delete the selected folders?")
        msg.setWindowTitle("Confirmation")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            for i in reversed(selected_rows):
                folder_path = self.table.item(i, 2).text()
                os.rmdir(folder_path)
                self.table.removeRow(i)

    def toggle_checkboxes(self):
        checked = self.header_checkbox.isChecked()
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).layout().itemAt(0).widget().setChecked(checked)

    def on_header_clicked(self, logicalIndex):
        if logicalIndex == 0:
            if self.header_checkbox.isChecked():
                self.header_checkbox.setCheckState(Qt.Unchecked)
            else:
                self.header_checkbox.setCheckState(Qt.Checked)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and source is self.table.viewport():
            item = self.table.itemAt(event.pos())
            if item and item.isSelected():
                self.table.clearSelection()
                return True

        return super().eventFilter(source, event)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
