import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pandas as pd
import sqlite3
import subprocess
import argparse
import sqlboiler

parser = argparse.ArgumentParser(description='Process selected rows')
parser.add_argument('rows', nargs='+', help='Selected rows')

# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
stylesfolder = current_dir + "/styles/"


currstyle = sqlboiler.getstyle(db_path)
style_path = os.path.join(stylesfolder, currstyle)

class FolderValidator(QValidator):
    def validate(self, input_str, pos):
        if os.path.isdir(input_str):
            return (QValidator.Acceptable, input_str, pos)
        elif input_str == "":
            return (QValidator.Intermediate, input_str, pos)
        else:
            return (QValidator.Invalid, input_str, pos)


class FileTypeValidator(QValidator):
    def __init__(self, file_ext):
        super().__init__()
        self.file_ext = file_ext
        
    def validate(self, input_str, pos):
        if input_str.endswith(self.file_ext) and os.path.isfile(input_str):
            return (QValidator.Acceptable, input_str, pos)
        elif input_str == "":
            return (QValidator.Intermediate, input_str, pos)
        else:
            return (QValidator.Invalid, input_str, pos)

class UI(QWidget):

    def __init__(self):
        super().__init__()
        args = parser.parse_args()
        self.selected_rows = args.rows
        self.insup = 0

        # create a layout
        layout = QVBoxLayout()

        # Add a label at the top of the window
        self.label1 = QLabel('Please input/update/accept values for number of images, shotlist file,image save folder')
        
        self.label1.setStyleSheet("font-size: 18pt; font-family: Courier; font-weight: bold;")
        
        # create a connection to the database
        self.connection = sqlite3.connect(db_path)
        sql= 'SELECT s.ShotlistID, s.productionid, s.numberofimages, s.ShotlistPath, s.shotlistimagesfolder FROM shotlists s where s.productionid=' + self.selected_rows[0]#self.productionid[0]
        
        # create a dataframe from the data in the database
        self.df = pd.read_sql_query(sql, self.connection)
        castsql= f"""SELECT CastlistPath FROM castlists c where c.productionid= {self.selected_rows[0]} """
        self.castdf = pd.read_sql_query(castsql, self.connection)
        
        self.num_images_edit =QLineEdit(str(0))
        self.shotlist_edit =QLineEdit('')
        self.save_folder_edit = QLineEdit('')
        self.num_images_label = QLabel('Number of Images:(1-50)')
        self.cast_list_edit = QLineEdit('')
        if not self.df.empty:
            self.insup =1
            self.num_images_edit = QLineEdit(str(self.df.iloc[0]['numberofimages']))
            self.num_images_edit.setValidator(QIntValidator())
            self.shotlist_edit = QLineEdit(self.df.iloc[0]['ShotlistPath'])
            self.shotlist_edit.setReadOnly(True)
            self.save_folder_edit = QLineEdit(self.df.iloc[0]['ShotlistImagesFolder'])
            self.save_folder_edit.setReadOnly(True)
            if not self.castdf.empty:
                self.cast_list_edit = QLineEdit(self.castdf.iloc[0]['CastlistPath'])
                self.cast_list_edit.setReadOnly(True)

        self.shotlist_label = QLabel('Shotlist File:(csv file)')
        
        self.shotlist_browse = QPushButton('Browse')
        self.shotlist_browse.clicked.connect(self.browse_shotlist_file)
        
        self.save_folder_label = QLabel('Save Folder:')
        
        self.save_folder_browse = QPushButton('Browse')
        self.save_folder_browse.clicked.connect(self.browse_save_folder)

        self.cast_list_label = QLabel('Cast List:(csv file)')
        
        self.cast_list_browse = QPushButton('Browse')
        self.cast_list_browse.clicked.connect(self.browse_cast_list)

        validator = QIntValidator(1,50,self)
        self.num_images_edit.setValidator(validator)

        folvalidator = FolderValidator(self)
        self.save_folder_edit.setValidator(folvalidator)

        # Set validator for textbox to only accept a valid file path for a specific file type
        file_type = ".csv" 
        filevalidator = FileTypeValidator(file_type)
        self.shotlist_edit.setValidator(filevalidator)
        self.cast_list_edit.setValidator(filevalidator)

        # add the labels and textboxes to the layout
        layout.addWidget(self.label1)
        layout.addWidget(self.num_images_label)
        layout.addWidget(self.num_images_edit)
        layout.addWidget(self.shotlist_label)
        layout.addWidget(self.shotlist_edit)
        layout.addWidget(self.shotlist_browse)
        layout.addWidget(self.save_folder_label)
        layout.addWidget(self.save_folder_edit)
        layout.addWidget(self.save_folder_browse)
        layout.addWidget(self.cast_list_label)
        layout.addWidget(self.cast_list_edit)
        layout.addWidget(self.cast_list_browse)

        # set the layout for the widget
        self.setLayout(layout)

        # in the __init__ method, create the button and connect it to the update_data function
        self.update_button = QPushButton('Continue')
        self.update_button.clicked.connect(self.update_data)
        layout.addWidget(self.update_button)

        # Connect the textChanged signals of text boxes to a slot that enables/disables the button
        self.save_folder_edit.textChanged.connect(self.enable_button)
        self.shotlist_edit.textChanged.connect(self.enable_button)
        self.cast_list_edit.textChanged.connect(self.enable_button)

        # Connect the textChanged signal of the text box to a slot that enables/disables the button
        self.num_images_edit.textChanged.connect(self.enable_button)

        # Disable the button initially
        self.update_button.setEnabled(False)

        # Load the style sheet
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())

    def enable_button(self):
        # Enable the button only if all validators are valid
        if self.save_folder_edit.hasAcceptableInput() and self.shotlist_edit.hasAcceptableInput() \
        and self.num_images_edit.hasAcceptableInput() and self.cast_list_edit.hasAcceptableInput():
            self.update_button.setEnabled(True)
        else:
            self.update_button.setEnabled(False)

    def browse_shotlist_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', current_dir, 'CSV files (*.csv)')
        if filename:
            self.shotlist_edit.setText(filename[0])

    def browse_save_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, 'Open Folder', current_dir)
        if foldername:
            self.save_folder_edit.setText(foldername)

    def browse_cast_list(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', current_dir, 'CSV files (*.csv)')
        if filename:
            self.cast_list_edit.setText(filename[0])

    def update_data(self):
        # get the data from the text boxes
        num_images = self.num_images_edit.text()
        shotlist_file = self.shotlist_edit.text()
        save_folder = self.save_folder_edit.text()
        cast_file = self.cast_list_edit.text()

        #check does castlist exist
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        castsql= f"""SELECT castlistID FROM castlists c where c.productionid= {self.selected_rows[0]} """ #and c.CastlistPath= '{cast_file}'"""
        
        # create a dataframe from the data in the database
        cursor.execute(castsql)
        castlist_result = cursor.fetchone()
        
        if castlist_result is None:
           
            cursor.execute('''INSERT INTO castlists (productionID, CastlistPath) VALUES (?, ?)''', (self.selected_rows[0], cast_file))
            castlist_id = cursor.lastrowid
            
        else:
            castlist_id = castlist_result[0]
            cursor.execute('''UPDATE castlists SET CastlistPath=? WHERE CastListID=?''', (cast_file, castlist_id))
            
        castcsvdf = pd.read_csv(cast_file)

        # iterate through the rows of the DataFrame
        for index, row in castcsvdf.iterrows():
            # access the values in each column of the row using the column name
            col1_value = row['Cast Name']
            
            rolesql= f"""SELECT roleid FROM roleactor r where r.CastListID= {castlist_id} and r.rolename= '{col1_value}'"""
            
            cursor.execute(rolesql)
            role_result = cursor.fetchone()
            if role_result ==None:
                
                cursor.execute('''INSERT INTO roleactor(rolename, CastListID ) VALUES (?, ?)''', (col1_value, castlist_id))
            
        if self.insup == 0:
            cursor.execute('''INSERT INTO Shotlists (productionID, numberofimages, shotlistpath, shotlistimagesfolder) VALUES (?, ?, ?, ?)''', (self.selected_rows[0], num_images, shotlist_file, save_folder))
        else:
            cursor.execute('''UPDATE Shotlists SET numberofimages=?, shotlistpath=?, shotlistimagesfolder=? WHERE productionID=?''', (num_images, shotlist_file, save_folder, self.selected_rows[0]))
        connection.commit()
        connection.close()

        # update the data displayed in the UI
        self.num_images_edit.setText(num_images)
        self.shotlist_edit.setText(shotlist_file)
        self.save_folder_edit.setText(save_folder)
        ui.hide()
        subprocess.run(['python', current_dir + '/roleactor_settings4.py'] + ['--castlistid', str(castlist_id)] + ['--prodid', str(self.selected_rows[0])])
        QApplication.quit()

    def showEvent(self, event):
        super().showEvent(event)
        self.enable_button()  # Enable/disable button based on initial state of line edit
        


app = QApplication(sys.argv)
ui = UI()
ui.show()
sys.exit(app.exec_())
