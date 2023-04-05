# Aubrushli_images
An Image Generator utilising Stable Diffusion

* Very much a work in progress, no guarantees at all.

Aubrushli Images takes a shot list and cast list generated by [Aubrushli](https://github.com/StephanosPSteer/AUBRUSHLI) and creates images that can be used by the storyboard part of Aubrushli, but the images are just normal PNGs so can be used maybe for a pitchdeck or set inspiration or for whatever.
Stable Diffusion itself and any of its front ends have a million more features than this, however I aim to give this over time the specific goal of turning a shot lists into storyboard almost automatically and that means focussing on the interpretation of scripts and screenplays into prompts. 

The actual integration with stable diffusion is pretty light and therefore any updates or perhaps utilising other image generators in the future should be fairly easy to incorporate.

# So what does this do?

Well the process is:-  
 
1) Run the python file productions.py

![aub_imgs1](https://user-images.githubusercontent.com/26924183/229894501-d1fe1c5f-eba6-45ff-9e0c-3a0933fdc225.png)

2) Create a production name

![aub_imgs2](https://user-images.githubusercontent.com/26924183/229894856-686e6f19-16b3-40f7-b819-2247826a0ae0.png)

![aub_imgs3](https://user-images.githubusercontent.com/26924183/229895039-ae1c6738-cb08-44c9-8a30-3523512e34fc.png)

3) Choose the number of images per shot, associate an aubrushli formatted Shot list, cast list and save folder with that production.

![aub_imgs4](https://user-images.githubusercontent.com/26924183/229895277-5e80ca1a-4f33-4816-9d74-8e2505cd9882.png)

![aub_imgs5](https://user-images.githubusercontent.com/26924183/229895671-5152d487-c034-4924-bacf-6d33a8d14bef.png)

4) Associate Characters with celebrities (although you could use whatever you want) to allow more consistent images.

![aub_imgs6](https://user-images.githubusercontent.com/26924183/229896101-e3897acf-14e1-47b8-b620-ab769ba1b893.png)

![aub_imgs7](https://user-images.githubusercontent.com/26924183/229896141-1d0e9a20-d853-4595-86ce-2db14a942062.png)

5) Then choose which shots to create images for

![aub_imgs8](https://user-images.githubusercontent.com/26924183/229896403-7f0ce52d-e802-4e51-8647-2bec586b65a4.png)

![aub_imgs9](https://user-images.githubusercontent.com/26924183/229896724-cab6a046-1ead-424e-aeb8-f15a0396dc76.png)

6) And wait (hopefully not too long but it depends on your hardware - for me an image every 4 seconds approx)

![aub_imgs10](https://user-images.githubusercontent.com/26924183/229897060-d5e84860-6106-4145-8c3d-056911e1a565.png)

7) Ta da!! although here you see some of the failings, this is meant to be a medium shot but it is wide most of the time and obviously some of the other issues with SD are apparent e.g. artefacts and multiples. Nevertheless in my opinion even if you can't immediately get a good storyboard image, just the selection of images gives ideas for set design, wardrobe and possible shot selection, not to mention possibly pitch decks.

![aub_imgs11](https://user-images.githubusercontent.com/26924183/229897543-3b2cca9f-0af5-448e-80ae-fc2c1b86a404.png)

# Speaking of Hardware

It is really the hardware requirements for [stable diffusion](https://github.com/AUTOMATIC1111/stable-diffusion-webui) which says "4GB video card support (also reports of 2GB working)" so that, you need at least an ok graphics card or a Mac m1/m2, the only thing I have tested on is a Windows PC with an Nvidia 3090


# What it won't let you do

Most stable diffusion things. Not even changing CFG_Scale (I leave at default, the thing is I figure if you are using for storyboards you just want to use it and not get too involved in the frankly a bit unpredictable cfg_scale). At the moment Image aspect ratio is wider than the normal 512 x 512 (if not quite 16:9). This is because this is aimed at storyboards and most will be wide screen. This may well cause issues on lower hardware. I havent added any controlnet features or actually any img to img because the idea is to get it directly from a shot list. Thats not to say it won't look a million times better so maybe later I will try and incorporate those options. I looked at Gligen and at composable diffusion/latent couple as I thought they could be very useful but right now if I use a wider format they tend to create multiples much more than normal which defeats the purpose of a composable image. I want to properly incorporate Seeds as I think that will be useful for a consistent look across shots and that is my very next thing to do.


## Brief suggested install process

+ Create a conda environment. I used python 3.10
+ Activate
+ git clone the above repo to a local folder or if you have a SD local installation, then install there as it should work without having to again install stable diffusion as long as its in the same directory as the model files. NOTE will look at adding a path setting so this is easier. 
+ pip install PyQt5
+ conda install pandas
+ conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia ******DEPENDS ON SYSTEM BUT INSTALL PYTORCH******
+ pip install diffusers
+ pip install git+https://github.com/huggingface/transformers ******************NEED TRANSFORMERS FROM SOURCE ******************
+ pip install accelerate

Then you need to go and get folders and files from Stability AI. The one I used was at hugging face https://huggingface.co/stabilityai/stable-diffusion-2-1/tree/main

However I realise that I can reduce this down substantially by not using the safetensors files:- below is the folders and files I am using. Most of them are from that huggingface repository but the really cut back model is from https://huggingface.co/stabilityai/sd-vae-ft-mse-original/blob/main/vae-ft-mse-840000-ema-pruned.ckpt and the qss sheet is from https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss 

![AUb_images](https://user-images.githubusercontent.com/26924183/229891129-cbdc51c9-782f-44a2-908d-8fdac2ad46ab.png)

# TODO LIST
+ Change the gss stylesheet file in settings. as I am currently forcing people to use [this](https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss)
+ Let people choose model in the app. The app currently selects whichever model is in the current folder.
+ Selectable SEEDS so that you can get a consistent look across storyboards.
+ Investigate incorporating seed, prompt and model used into image metadata.
+ Allow changing image size/aspect ratio
+ Maybe CFG_Scale but perhaps just change to best replicate prompt.
+ Make it look a lot better.
+ Incorporate Gligen or Composable diffusion/latent couple.
+ Hook it up properly with Aubrushli itself and indeed with the StoryBoard Module.
+ Clean up code, wasn't planning on a full app it just is increasingly going that way and right now spaghetti and technical debt is increasing. 

Anyway thats the initial readme, lots to add, watch this space. 
