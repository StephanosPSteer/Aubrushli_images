import csv
import sys
import subprocess
import sqlite3
import os
import argparse
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox
import sqlboiler
# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
stylesfolder = current_dir + "/styles/"



currstyle = sqlboiler.getstyle(db_path)
style_path = os.path.join(stylesfolder, currstyle)

class CSVWindow(QMainWindow):
    def __init__(self, filename, prodid, castlistid):
        super().__init__()
        self.filename = filename
        self.prodid = prodid
        self.castlistid = castlistid
        self.rows = []
        self.initUI()
        
    def initUI(self):
        # Create a central widget and a vertical layout
        central_widget = QWidget()
        vbox = QVBoxLayout()
        
        # Add a label at the top of the window
        label = QLabel('Please select shots that you want to create images for:')
        label.setStyleSheet("font-size: 18pt; font-family: Courier; font-weight: bold;")
        vbox.addWidget(label)
        
        # Read the CSV file and create a checkbox for each row
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                row_text = ', '.join([row['Description'], row['Scene Number'], row['Scene Name'], row['Shot Size'], row['Shot Type'], row['AngleOrigin'], row['MoveMent'], row['lens'] ])
                checkbox = QCheckBox(f"SHOT {row['Shot Number']}: {row_text}")
                vbox.addWidget(checkbox)
                self.rows.append((row['Shot Number'], row, checkbox))
        
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
    parser = argparse.ArgumentParser(description='castlistid')
    parser.add_argument('--castlistid', nargs='+', help='castlistid')
    parser.add_argument('--prodid', nargs='+', help='castlistid')
    args = parser.parse_args()
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    prodid = str(args.prodid[0])
    castlistid = str(args.castlistid[0])
    c.execute('''SELECT * FROM Shotlists where productionid=?''',(prodid,))
    settings_data = [dict(row) for row in c.fetchall()]

    for row in settings_data:
        shot_list_file = row["ShotlistPath"]
        
    conn.close()
 
    csv_window = CSVWindow(shot_list_file, prodid, castlistid)
    csv_window.show()
    sys.exit(app.exec_())

