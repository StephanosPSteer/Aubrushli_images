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


parser = argparse.ArgumentParser(description='Process selected rows')
parser.add_argument('--shots', nargs='+', help='Selected rows')
parser.add_argument('--prodid', nargs='+', help='output directory')
parser.add_argument('--castlistid', nargs='+', help='castlistid')

# get the current file's directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# navigate to the desired file's path relative to the current directory
db_path = os.path.join(current_dir, 'aubrushli.db')
style_path = os.path.join(current_dir, 'dark_orange3.qss')

if __name__ == '__main__':
    args = parser.parse_args()
    selected_shots = args.shots
    prodid = args.prodid[0]
    castlistid = args.castlistid[0]
    
SDV5_MODEL_PATH = current_dir
pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

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
    
    g_cpu = torch.Generator()
    
    # Create the directory if it does not exist
    if not os.path.exists(directory_path):
         os.makedirs(directory_path)
         print("Directory created successfully!")
    else:
        print("Directory already exists.")


    next_number = len( os.listdir(directory_path) ) + 1
    for pics in range(next_number, next_number + myimages):
        with autocast("cuda"):
            seed = random.randint(1, 2147483647)
            generator = torch.Generator("cuda").manual_seed(seed)
            image = pipe(prompt, negative_prompt=negative_prompt, height=536, width=768, generator=generator).images[0]
            imgpath = directory_path + "/" + "shot" + shot + "_" + str(pics) + "_SEED" + str(seed) + ".png"
            metadata = PngInfo()
            metadata.add_text("prompt", str(prompt))
            metadata.add_text("seed", str(seed))
            image.save(imgpath, pnginfo=metadata)
            targetImage = Image.open(imgpath)
    pics+=1
