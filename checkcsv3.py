import csv
import sys
import subprocess
import sqlite3
import os
import argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox
import sqlboiler
import pathboiler
import pandas as pd

current_dir,db_path = pathboiler.getkeypaths()
stylesfolder, currstyle, style_path = pathboiler.getstylepaths()
parser = argparse.ArgumentParser(description='castlistid')
parser.add_argument('--castlistid', nargs='+', help='castlistid')
parser.add_argument('--prodid', nargs='+', help='castlistid')


class CSVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        args = parser.parse_args()
        self.seeded = 0
        shotlistfile, seed, num_images, save_folder = sqlboiler.getshotlist(str(args.prodid[0]))
        if pd.isnull(seed) or seed is None or len(str(seed).strip()) == 0:
            self.seed = ""
            #print("its null")
        else:
            self.seed = seed
            self.seeded = 1
            #print("its not null")
        
        self.filename = shotlistfile
        self.prodid = str(args.prodid[0])
        self.castlistid = args.castlistid[0]
        
        self.rows = []
        self.initUI()
        
    def initUI(self):
        # Create a central widget and a vertical layout
        central_widget = QWidget()
        vbox = QVBoxLayout()
        
        # Add a label at the top of the window check if seeded
        if self.seeded == 0:
            labtext = 'Please select shots that you want to create images for:'
        else:
            labtext = "As you have chosen a seed all shots are preselected and one image will be produced for each, you can unselect shots you don't want"

        label = QLabel(labtext)
        #label.setStyleSheet("font-size: 18pt; font-family: Courier; font-weight: bold;")
        vbox.addWidget(label)
        
        # Read the CSV file and create a checkbox for each row
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                row_text = ', '.join([row['Description'], row['Scene Number'], row['Scene Name'], row['Shot Size'], row['Shot Type'], row['AngleOrigin'], row['MoveMent'], row['lens'] ])
                checkbox = QCheckBox(f"SHOT {row['Shot Number']}: {row_text}")
                vbox.addWidget(checkbox)
                self.rows.append((row['Shot Number'], row, checkbox))
        
        # check all the rows for when seed happens
        if len(str(self.seed).strip())> 0:
            print(self.seed)
            for i in range(vbox.count()):
                widget = vbox.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    widget.setChecked(True)

        
        # Create a horizontal layout for the confirm button
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        confirm_button = QPushButton('Confirm')
        hbox.addWidget(confirm_button)
        
        # Add the horizontal layout to the vertical layout
        vbox.addLayout(hbox)
        
        # Set the central widget and the layout
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        
        # Connect the confirm button to the handler function
        confirm_button.clicked.connect(self.confirmSelection)
        
        # Load the style sheet
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())
        
    def confirmSelection(self):
        selected_rows = []
        #print(self.rows)
        for row in self.rows:
            #print(row)
            if row[2].isChecked():
                #print(row)
                selected_rows.append(row[0])
                print(selected_rows)
        if not selected_rows:
            # Show an error message if no row is selected
            QMessageBox.critical(self, 'Error', 'No row selected. Please select at least one row before confirming.')
        else:
            csv_window.hide()
            subprocess.run(['python', current_dir + '/create_images2.py'] + ['--shots'] + selected_rows + ['--prodid',  str(self.prodid), '--castlistid', str(self.castlistid)] )
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    csv_window = CSVWindow()
    csv_window.show()
    sys.exit(app.exec_())
