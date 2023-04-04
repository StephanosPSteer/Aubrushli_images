import os
import random
import pandas as pd
import torch
import sqlite3
from torch import autocast
from diffusers import StableDiffusionPipeline
import argparse
import re
import json
import copy

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
highest_number = 0
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

    # # Connect to the SQLite database
    # conn = sqlite3.connect(db_path)
    # c = conn.cursor()
    # # Retrieve the rows with the matching shot size from the database
    # query = f"SELECT xstart, ystart, xend, yend FROM locationdata WHERE LOWER(shot_size) = LOWER('{shot_size}')"
    # #print(query) # Print the query with shot_size included      
    # c.execute(query)



    # #c.execute("SELECT xstart, ystart, xend, yend FROM locationdata WHERE shot_size = ?", (shot_size,))
    # results = c.fetchall()
    # # Put the values into a Pandas DataFrame
    # #newdf = pd.DataFrame(rows, columns=['xstart', 'ystart', 'xend', 'yend'])
    # #print(newdf)
    # # Convert the results to an array of decimals
    # locations_array =[]
    # location_array = []
    # for row in results:
    #     location_array.append([float(val) for val in row])


    # locations_array.append(location_array)
    
    for row in role_actor_data:
      desc = re.sub(r'(?i)\b{}\b'.format(re.escape(row["rolename"])), row["actorname"], desc)
    
    # rolearry = []
    # for performer in role_actor_data:
    #     if performer["actorname"] in desc:
    #         rolearry.append(performer["actorname"])
    
    # if len(rolearry) > 1:
    #     for i in range(1, len(rolearry)): 
            
    #         location = copy.deepcopy(location_array)
    #         thediff = location[0][2] - location[0][0]
    #         location[0][0] = (location[0][0]) * (i+1)
    #         location[0][2] = location[0][0] + thediff
    #         locations_array = locations_array[:] + [location]
   
    #json_data = json.dumps(locations_array)
    shot_size = shot_size.replace("W","Wide")
    shot_size = shot_size.replace("M","Medium")
    shot_size = shot_size.replace("CU","Close Up")
    prompt = shot_size + ',' + desc + ',' + scenename + ',' + lens + "mm," + angle + ',' + shot_type + ',' + move + ',' + "black & white,pencil sketch,hyper realistic,intricate sharp details,smooth,colorful background"
    
    # Define the path of the directory you want to create
    directory_path = topdir + "/shot" + shot
    
    g_cpu = torch.Generator()
    
    # Create the directory if it does not exist
    if not os.path.exists(directory_path):
         os.makedirs(directory_path)
         print("Directory created successfully!")
    else:
        print("Directory already exists.")
         # Loop through each file in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.png'):  # Check if the file is a PNG file
                 
                file_number = int(filename.split('_')[-1].split('.')[0])  # Extract the number after the underscore
                # Check if the number is higher than the current highest number
                if file_number > highest_number:
                    highest_number = file_number
        next_number = highest_number + 1  # Assign a variable with a value of one more than the highest number
        print("The highest number found in the directory is:", highest_number)
        print("The next number to use is:", next_number)


    for pics in range(next_number, next_number + myimages):
        with autocast("cuda"):
            seed = random.randint(1, 2147483647)
            generator = torch.Generator("cuda").manual_seed(seed)
            image = pipe(prompt, negative_prompt=negative_prompt, height=536, width=768, generator=generator).images[0]
            imgpath = directory_path + "/" + "shot" + shot + "_" +str(pics) +".png"
            image.save(imgpath)
    pics+=1