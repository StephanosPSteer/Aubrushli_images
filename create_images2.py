import os
import random
import pandas as pd
import torch
import sqlite3
from torch import autocast
from diffusers import StableDiffusionPipeline#, AutoencoderKL
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
import pathboiler  

parser = argparse.ArgumentParser(description='Process selected rows')
parser.add_argument('--shots', nargs='+', help='Selected rows')
parser.add_argument('--prodid', nargs='+', help='output directory')
parser.add_argument('--castlistid', nargs='+', help='castlistid')

current_dir,db_path = pathboiler.getkeypaths()
stylesfolder, currstyle, style_path = pathboiler.getstylepaths()


class ImageGeneratorThread(QThread):
    new_image = pyqtSignal(str)  # signal to emit when a new image is generated
    
    def __init__(self, imgdf):
        super().__init__()
        self.imdf = imgdf
        
    def run(self):

        #imdf

        for index, row in self.imdf.iterrows():
            directory_path = row['directory_path']
            myimages = row['myimages']
            prompt = row['prompt']
            negative_prompt = row['negative_prompt']
            shot = row['shot']
            myseed = row['preferredseed']
            #print(f"Name: {name}, Age: {age}, Country: {country}")

            SDV5_MODEL_PATH = current_dir
            pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH, torch_dtype=torch.float16)   
            pipe = pipe.to("cuda")
            
            next_number = len(os.listdir(directory_path)) + 1
            for pics in range(next_number, next_number + myimages):
                with autocast("cuda"):
                    if pd.isnull(myseed) or myseed is None or len(str(myseed).strip()) == 0:
                        seed = random.randint(1, 2147483647)
                    else:
                        print(myseed)
                        seed = int(myseed)
                    generator = torch.Generator("cuda").manual_seed(seed)
                    image = pipe(prompt, negative_prompt=negative_prompt, guidance_scale=15, height=512, width=768, generator=generator).images[0]
                    imgpath = directory_path + "/" + "shot" + shot + "_" + str(pics) + "_SEED" + str(seed) + ".png"
                    metadata = PngInfo()
                    metadata.add_text("prompt", str(prompt))
                    metadata.add_text("seed", str(seed))
                    image.save(imgpath, pnginfo=metadata)
                    print(imgpath)
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

          

        def start_image_generation(self, imgdf):
            
            if self.thread is not None and self.thread.isRunning():
           
                return  # don't start a new thread if one is already running
            
           
            
            self.thread = ImageGeneratorThread(imgdf)
            self.thread.new_image.connect(self.save_image)
            self.thread.start()
        
def main():
        app = QApplication(sys.argv)
        window = MainWindow()

        args = parser.parse_args()
        selected_shots = args.shots
        prodid = args.prodid[0]
        castlistid = args.castlistid[0]
        columns = ['directory_path', 'myimages', 'prompt', 'negative_prompt', 'shot']
        imagesdf = pd.DataFrame(columns=columns)
        
        

        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        shot_list_file, PreferredSeed, num_images, save_folder = sqlboiler.getshotlist(prodid)

        # Select data from roleactor table
        c.execute('''SELECT * FROM roleactor where castlistid=? AND actorname IS NOT NULL AND LENGTH(actorname) > 0''',(castlistid,))
        role_actor_data = [dict(row) for row in c.fetchall()]
        # Close the database connection
        conn.close()

        #if I have a seed then only one image of each shot
        if pd.isnull(PreferredSeed) or PreferredSeed is None or len(str(PreferredSeed).strip()) == 0:
            myimages = num_images
        else:
            myimages = 1
        print(myimages)
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
            shot_size = shot_size.replace("M","Close Up")
            shot_size = shot_size.replace("CU","Extreme Close Up")
            prompt =  shot_size + ',' + desc + ',' + scenename  + ',' + lens + "mm," + angle + ',' + shot_type + ',' + move + ',' + "black & white,pencil sketch,hyper realistic,intricate sharp details,smooth,colorful background"
            
            # Define the path of the directory you want to create
            directory_path = topdir + "/shot" + shot
            
            
            
            # Create the directory if it does not exist
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print("Directory created successfully!")
            else:
                print("Directory already exists.")


                #columns = ['directory_path', 'myimages', 'prompt', 'negative_prompt', 'shot']
                #imagesdf = pd.DataFrame(columns=columns)
            
            # name = input('Enter a name: ')
            # age = int(input('Enter an age: '))
            # country = input('Enter a country: ')

            print(myimages)
            data = {'directory_path': directory_path, 'myimages': myimages, 'prompt': prompt, 'negative_prompt': negative_prompt, 'shot': shot, 'preferredseed': PreferredSeed }
            imagesdf= imagesdf.append(data, ignore_index=True)

        print(imagesdf)    
        window.start_image_generation(imagesdf)
           


    
        sys.exit(app.exec_())   

if __name__ == '__main__':
     main()

        




    # Run the application
#sys.exit(app.exec_())
