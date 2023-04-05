import sys
import os
from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QApplication, QPushButton
import argparse
import subprocess
import sqlite3

parser = argparse.ArgumentParser(description='castlistid')
parser.add_argument('--castlistid', nargs='+', help='castlistid')
parser.add_argument('--prodid', nargs='+', help='castlistid')
args = parser.parse_args()

# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
stylesfolder = current_dir + "/styles/"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()
stylesql= f"SELECT stylesheetpath FROM settings" 
cursor.execute(stylesql)
currstyle = cursor.fetchone()[0]
connection.commit()
connection.close()

style_path = os.path.join(stylesfolder, currstyle)

class MainWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)

         # Connect to database
        self.__database__ = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.__database__.setDatabaseName(db_path)
        self.__database__.open()

        # Create QComboBox to show tables
        self.__tableNames__ = QtWidgets.QComboBox(self)
        self.__tableGrid__ = QtWidgets.QTableView(self)
      
        # Create table model 
        self.__tableModel__ = QtSql.QSqlTableModel(self, self.__database__)
        self.__tableGrid__.setModel(self.__tableModel__)

         # Connect combobox signal to update model
        self.__tableNames__.currentIndexChanged[str].connect(self.__tableModel__.setTable)
        self.__tableNames__.currentIndexChanged[str].connect(self.__tableModel__.select)
        self.__tableNames__.currentIndexChanged[str].connect(self.hideColumns)

        # Filter tables
        table_filters = ['roleactor']
        tables = [t for t in self.__database__.tables() if any(f.lower() in t.lower() for f in table_filters)]

        # Set the list of the tables to combobox
        self.__tableNames__.addItems(tables)
                 
        # Filter the rows of the model
        filter_str = "CastListID =" + args.castlistid[0]
        self.__tableModel__.setFilter(filter_str)

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__tableNames__)
        layout.addWidget(self.__tableGrid__)

        # in the __init__ method, create the button and connect it to the update_data function
        self.update_button = QPushButton('Continue')
        self.update_button.clicked.connect(self.RunCheckCSV)
        layout.addWidget(self.update_button)

        # Set the layout for the window
        self.setLayout(layout)

        # Load the style sheet
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())

    def hideColumns(self):
        self.__tableGrid__.setColumnHidden(0, True)
        self.__tableGrid__.setColumnHidden(1, True)

    def RunCheckCSV(self):
        ui.hide()
        subprocess.run(['python', current_dir + '/checkcsv3.py'] + ['--castlistid', str(args.castlistid[0])] + ['--prodid', str(args.prodid[0])])
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
