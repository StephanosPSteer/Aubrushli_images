import os
import random
import pandas as pd
import torch
import sqlite3
from torch import autocast
from diffusers import StableDiffusionPipeline
import argparse
import re
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from PyQt5 import QtWidgets, QtGui
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import QThread, pyqtSignal
import json
import sqlboiler  



parser = argparse.ArgumentParser(description='Process selected rows')
parser.add_argument('--shots', nargs='+', help='Selected rows')
parser.add_argument('--prodid', nargs='+', help='output directory')
parser.add_argument('--castlistid', nargs='+', help='castlistid')

# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
stylesfolder = current_dir + "/styles/"
currstyle = sqlboiler.getstyle(db_path)
style_path = os.path.join(stylesfolder, currstyle)


class ImageGeneratorThread(QThread):
    new_image = pyqtSignal(str)  # signal to emit when a new image is generated
    
    def __init__(self, directory_path, myimages, prompt, negative_prompt, shot):
        super().__init__()
        self.directory_path = directory_path
        self.myimages = myimages
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.shot = shot
        
    def run(self):

        SDV5_MODEL_PATH = current_dir
        pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH, torch_dtype=torch.float16)
        pipe = pipe.to("cuda")
        #g_cpu = torch.Generator()
        next_number = len(os.listdir(self.directory_path)) + 1
        for pics in range(next_number, next_number + self.myimages):
            with autocast("cuda"):
                seed = random.randint(1, 2147483647)
                generator = torch.Generator("cuda").manual_seed(seed)
                image = pipe(self.prompt, negative_prompt=self.negative_prompt, height=536, width=768, generator=generator).images[0]
                imgpath = self.directory_path + "/" + "shot" + self.shot + "_" + str(pics) + "_SEED" + str(seed) + ".png"
                metadata = PngInfo()
                metadata.add_text("prompt", str(self.prompt))
                metadata.add_text("seed", str(seed))
                image.save(imgpath, pnginfo=metadata)
               
                self.new_image.emit(imgpath)  # emit the signal with the path of the new image
                
            pics += 1


class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
            self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
            self.vbox = QVBoxLayout()               # The Vertical Box that contains the 
            self.testlab = QLabel("As images are generated you should start seeing them below along with the prompt text and seed value")
            self.testlab.setWordWrap(True)
            self.testlab.setAlignment(Qt.AlignLeft)
            self.testlab.setAlignment(Qt.AlignTop)
            self.vbox.addWidget(self.testlab)
          

            self.thread = None
            self.widget.setLayout(self.vbox)

            #Scroll Area Properties
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setWidgetResizable(True)
            self.scroll.setWidget(self.widget)

            self.setCentralWidget(self.scroll)

            self.setGeometry(600, 100, 1000, 900)
            self.setWindowTitle('Generating Images')
                    # Load the style sheet
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
            
            self.show()


#             
        def save_image(self, imgpath):
            pixmap = QPixmap(imgpath)
            #pixmap = QtGui.QPixmap(imgpath).scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            object = QLabel()
            object.setPixmap(pixmap)
            targetImage = Image.open(imgpath)
            #print(targetImage.text)
            img_str = json.dumps(targetImage.text)
            infolab = QLabel(img_str)
            #self.layout.addWidget(self.imagelabel)
            self.vbox.addWidget(object)
            self.vbox.addWidget(infolab)

          

        def start_image_generation(self, directory_path, myimages, prompt, negative_prompt, shot):
            if self.thread is not None and self.thread.isRunning():
                return  # don't start a new thread if one is already running
            
            self.thread = ImageGeneratorThread(directory_path, myimages, prompt, negative_prompt, shot)
            self.thread.new_image.connect(self.save_image)
            self.thread.start()
        
def main():
        app = QApplication(sys.argv)
        window = MainWindow()

        args = parser.parse_args()
        selected_shots = args.shots
        prodid = args.prodid[0]
        castlistid = args.castlistid[0]
        
        

        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Select data from settings table
        c.execute('''SELECT * FROM Shotlists where productionid=?''',(prodid,))
        settings_data = [dict(row) for row in c.fetchall()]

        for row in settings_data:
            num_images = row["numberofimages"]
            shot_list_file = row["ShotlistPath"]
            save_folder = row["ShotlistImagesFolder"]

        # Select data from roleactor table
        c.execute('''SELECT * FROM roleactor where castlistid=? AND actorname IS NOT NULL AND LENGTH(actorname) > 0''',(castlistid,))
        role_actor_data = [dict(row) for row in c.fetchall()]
        # Close the database connection
        conn.close()

        myimages = num_images
        topdir = save_folder

        # Define the file path for your CSV file
        file_path = shot_list_file

        # Read the CSV file into a pandas DataFrame and assign the first row to the header row
        df = pd.read_csv(file_path, header=0)

        # Convert 'Shot Number' column to string
        df['Shot Number'] = df['Shot Number'].astype(str)

        # Convert values to string
        values = [str(val) for val in selected_shots]
        df_filtered = df[df['Shot Number'].isin(values)]

        negative_prompt = "(visible hand:1.3), (ugly:1.3), (duplicate:1.9),  (cloned face:1.9), (morbid:1.1), (mutilated:1.1), [out of frame], extra fingers, mutated hands, (poorly drawn hands:1.1), (poorly drawn face:1.2), (mutation:1.3), (deformed:1.3), (ugly:1.1), blurry, (bad anatomy:1.1), (bad proportions:1.2), (extra limbs:1.1), cloned face, (disfigured:1.2), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), (missing arms:1.1), (missing legs:1.1), (extra arms:1.2), (extra legs:1.2), mutated hands, (fused fingers), (too many fingers), (long neck:1.2)"
        negative_prompt = "duplicate, lowres, signs, memes, labels, text, food, text, error, mutant, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, made by children, caricature, ugly, boring, sketch, lacklustre, repetitive, cropped, (long neck), facebook, youtube, body horror, out of frame, mutilated, tiled, frame, border, porcelain skin, doll like, doll"
        next_number =0

        # Loop through each row in the DataFrame and access the values of each column by column name
        for index, row in df_filtered.iterrows():
            shot = str(row['Shot Number'])
            scene = str(row['Scene Number'])
            scenename = str(row['Scene Name'])
            shot_size = str(row['Shot Size'])
            shot_type = str(row['Shot Type'])
            angle = str(row['AngleOrigin'])
            move = str(row['MoveMent'])
            lens = str(row['lens'])
            desc = str(row['Description'])

        
            
            for row in role_actor_data:
                desc = re.sub(r'(?i)\b{}\b'.format(re.escape(row["rolename"])), row["actorname"], desc)
            

            shot_size = shot_size.replace("W","Wide")
            shot_size = shot_size.replace("M","Medium")
            shot_size = shot_size.replace("CU","Close Up")
            prompt =  desc + ',' + scenename + ',' + shot_size + ',' + lens + "mm," + angle + ',' + shot_type + ',' + move + ',' + "black & white,pencil sketch,hyper realistic,intricate sharp details,smooth,colorful background"
            
            # Define the path of the directory you want to create
            directory_path = topdir + "/shot" + shot
            
            
            
            # Create the directory if it does not exist
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print("Directory created successfully!")
            else:
                print("Directory already exists.")

            window.start_image_generation(directory_path, myimages, prompt, negative_prompt, shot)
           


    
        sys.exit(app.exec_())   

if __name__ == '__main__':
     main()

