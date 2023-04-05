import os
import sqlite3
import sys
import subprocess
from PyQt5.QtWidgets import QLineEdit, QApplication, QHBoxLayout, QMainWindow, QWidget, QVBoxLayout, QRadioButton, QLabel, QPushButton, QMessageBox 

# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
style_path = os.path.join(current_dir, 'dark_orange3.qss')

class foldWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.initUI()
        
    
    def sqlsel(self):
        conn = sqlite3.connect(db_path)
        # Query the table
        cursor = conn.execute("SELECT * from production")
        for i, row in enumerate(cursor):
              row_text = row
              self.radio_button = QRadioButton(f"PRODUCTION {i + 1}: {row_text}")
              self.vbox.addWidget(self.radio_button)
              self.rows.append((i + 1, row, self.radio_button))
        conn.close()


    def sqlins(self, prodname):
        # Connect to the database file or create it if it doesn't exist
        conn = sqlite3.connect(db_path)
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Define the data to insert
        ProductionName = prodname
        # Execute the insert query
        cursor.execute("INSERT INTO production (ProductionName) VALUES (?)", (ProductionName,))
        # Commit the transaction to the database
        conn.commit()
        # Close the database connection
        conn.close()
        self.rows = []
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.vbox = QVBoxLayout()
        # Add a label at the top of the window
        label = QLabel('Please select or Enter new production, then select')
        label.setStyleSheet("font-size: 18pt; font-family: Courier; font-weight: bold;")
        self.vbox.addWidget(label)
        self.sqlsel()

        # Create label for text box
        self.prodlabel = QLabel(self)
        self.prodlabel.setText("Enter New Production:")
        self.prodlabel.move(50, 50)

        # Create text box
        self.prodtext_box = QLineEdit(self)
        self.prodtext_box.move(50, 70)

        # Create button
        self.prodbutton = QPushButton("Add", self)
        self.prodbutton.move(50, 100)
        self.prodbutton.clicked.connect(self.add_production)

        self.vbox.addWidget(self.prodlabel)
        self.vbox.addWidget(self.prodtext_box)
        self.vbox.addWidget(self.prodbutton)

        # Create a horizontal layout for the confirm button
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        confirm_button = QPushButton('Continue')
        hbox1.addWidget(confirm_button)

        #vbox.addLayout(hbox)
        self.vbox.addLayout(hbox1)
        central_widget.setLayout(self.vbox)
        self.setCentralWidget(central_widget)

        # Connect the confirm button to the handler function
        confirm_button.clicked.connect(self.confirmSelection)

        # Load the style sheet
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())


    def add_production(self):
        # Get the value from the text box
        production = self.prodtext_box.text()

        # Add production to the SQL table
        self.add_to_database(production)

    def add_to_database(self, production):
        # Function to add data to SQL table
        self.sqlins(production)

    def confirmSelection(self, radio_button):
        selected_rows = []
        for row in self.rows:
            if row[2].isChecked():
                selected_rows.append(row[1][0])
        if not selected_rows:
            # Show an error message if no row is selected
            QMessageBox.critical(self, 'Error', 'No row selected. Please select at least one row before confirming.')
        else:
            # Call a second Python script and pass the selected rows as arguments
            nextwin = current_dir +  '\settings_window7.py'
            productionid = [str(val) for val in selected_rows]
            csv_window.hide()
            subprocess.run(['python', nextwin] + productionid)
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    csv_window = foldWindow()
    csv_window.show()
    sys.exit(app.exec_())
