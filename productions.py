import os
import sqlite3
import sys
import subprocess
from PyQt5.QtWidgets import QLineEdit, QApplication, QHBoxLayout, QMainWindow, QWidget, QVBoxLayout, QRadioButton, QLabel, QPushButton, QMessageBox, QComboBox, QGroupBox 
import sqlboiler
import pathboiler


current_dir,db_path = pathboiler.getkeypaths()
stylesfolder, currstyle, style_path = pathboiler.getstylepaths()

class foldWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stylesfolder = stylesfolder
        self.currentstyle =""
        self.rows = []
        self.initUI()
        
    
    def sqlsel(self):
        productions = sqlboiler.getallproduction()
        for i, row in productions.iterrows():
            radio_button = QRadioButton(f"Production: {row['ProductionName']}")
            self.vbox.addWidget(radio_button)
            self.rows.append((i + 1, row, radio_button))
        


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
        self.groupbox = QGroupBox("Group Box")
        self.vbox = QVBoxLayout()
     
        stylelabel = QLabel('Choose a style')
        self.vbox.addSpacing(10)
        self.dropdown = QComboBox()
        # Get a list of all the QSS files in the folder
        qss_files = [file for file in os.listdir(self.stylesfolder) if file.endswith(".qss")]

        # Add each QSS filename to the dropdown
        for file in qss_files:
            self.dropdown.addItem(file)
        
        self.dropdown.setCurrentText(currstyle)    
        self.vbox.addWidget(stylelabel)
        self.vbox.addWidget(self.dropdown)

        self.apply_button = QPushButton("Apply QSS")
        self.apply_button.clicked.connect(self.apply_qss)
        self.vbox.addWidget(self.apply_button)

        self.groupbox.setLayout(self.vbox)

        # Add a label at the top of the window
        label = QLabel('Please Select/Enter new production')
        
        self.vbox.addSpacing(10)
        self.vbox.addWidget(label)
        self.vbox.addSpacing(10)

        self.sqlsel()

        # Create label for text box
        self.prodlabel = QLabel(self)
        self.prodlabel.setText("Enter New Production:")
        self.prodlabel.move(50, 50)
        self.vbox.addSpacing(10)

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

       
        self.apply_qss()

    # Create a function to apply the selected QSS file to the window
    def apply_qss(self):
        qss_file = self.dropdown.currentText()
        currstyle = qss_file
        self.currentstyle = self.dropdown.currentText()
        qss_path = os.path.join(stylesfolder, qss_file)
        #print(qss_path)
        with open(qss_path, "r") as f:
            qss_data = f.read()
        #print(qss_data)
        app.setStyleSheet(qss_data)
        conn = sqlite3.connect(db_path)
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        cursor.execute("update settings set stylesheetpath=?", (qss_file,))
        # Commit the transaction to the database
        conn.commit()
        # Close the database connection
        conn.close()
        #print("Styles applied")

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
            subprocess.run(['python', nextwin] + productionid) #+ ['--style', self.currentstyle])
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    csv_window = foldWindow()
    csv_window.show()
    sys.exit(app.exec_())
