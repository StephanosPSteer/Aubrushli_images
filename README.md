# Aubrushli_images
An Image Generator utilising Stable Diffusion

* Very much a work in progress, no guarantees at all.

# Major Update - Now using [Controlnet - openpose](https://huggingface.co/lllyasviel/sd-controlnet-openpose)

Amazingly useful model and code. Now most of the time if a shot says its a close up the rendered image can be made to be a close up. The way I have coded the use of controlnet openpose is by creating a folder structure called shot_templates and under that structure there are folders that are named after common shot types. Within those folders I have put example images (some images are mine, others are creative commons from internet archive, google and bing and many are taken from the [Pexel people](https://huggingface.co/datasets/yuvalkirstain/pexel_people) dataset at hugging face. At the moment I am just choosing a random image from the specified shot type. Obviously this is not ideal and going forward I hope I can further subdivide the shot_template structure so that the storyboard image through the use of controlnet increasingly matches the description in the shotlist.

Controlnet does require further installation after the installs below [see here](https://huggingface.co/lllyasviel/sd-controlnet-openpose) but tbh it should just be pip install controlnet_aux and then when it runs it will download the required models. 

# Aubrushli_images description

Aubrushli Images takes a shot list and cast list generated by [Aubrushli2](https://github.com/StephanosPSteer/Aubrushli2) and creates images that can be used by the storyboard part of Aubrushli. The images are just normal PNGs so can be used for any number of reasons maybe for a pitchdeck or set inspiration, art design or to rethink shots etc etc.

Stable Diffusion web frontend and most of the third party frontends have lots more features than Aubrushli_images, this is because I aim to focus on the specific goal of turning shot lists into storyboards almost without any intervention and that means the key areas I will be looking at are the interpretation of scripts and screenplays into prompts, rather than reinventing the wheel. 

The actual integration with stable diffusion is pretty light and therefore any updates or possibly even utilising other image generators in the future should be fairly easy to incorporate.

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

Most stable diffusion configuration things. Not even changing CFG_Scale (I have set it at 15 as I want fairly realistic, the thing is I figure if you are using this its for storyboards, you just want to use it and not get too involved in the frankly a bit unpredictable cfg_scale). At the moment the image aspect ratio is wider than the normal (512 x 512 1:1) its 768 x 512 (Stability AI recommends at least one axis being 512) so not quite 16:9. This is because this is aimed at storyboards and most storyboards will be wide screen. This may well cause issues on lower hardware. 

~~I havent added any controlnet features or actually any img to img features because the idea is to get images directly from a shot list. Thats not to say it won't look a million times better if I do but it will be difficult to automate so maybe later I will try and incorporate those options.~~ 

I looked at [Gligen](https://github.com/gligen/GLIGEN) and at composable diffusion/latent couple as I thought they could be very useful, but right now if I use a wide image format they tend to create multiples even more than normal SD which defeats the purpose of a composable image. 

~~I want to properly incorporate Seeds as they will be useful for a consistent look across shots and that is my very next thing to do.~~ INCORPORATED


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

Then you need to go and get folders and files from Stability AI. The one I used was at [hugging face](https://huggingface.co/stabilityai/stable-diffusion-2-1/tree/main)

However I realise that I could reduce the download substantially by not using the safetensors files:- below is the folders and files I am using. Most of them are from that huggingface repository but the really cut back model is [here](https://huggingface.co/stabilityai/sd-vae-ft-mse-original/blob/main/vae-ft-mse-840000-ema-pruned.ckpt) and the qss sheet is from [here](https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss)

![AUb_images](https://user-images.githubusercontent.com/26924183/229891129-cbdc51c9-782f-44a2-908d-8fdac2ad46ab.png)

# Styles

I have added the ability to change styles and put a few stylesheets in the styles folder the extra styles come from [here](https://qss-stock.devsecstudio.com/templates.php)

# TODO LIST
+ ~~Change the qss stylesheet file in settings. as I am currently forcing people to use [this](https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss)~~
+ Let people choose model in the app. The app currently selects whichever model is in the current folder. ***This is actually not as trivial as it should be ***
+ ~~Selectable SEEDS so that you can get a consistent look across shots.~~ complete
+ ~~Investigate incorporating seed, prompt and model used into image metadata. I have added it, now to add a viewer to see it.~~
+ Allow changing image size/aspect ratio
+ Maybe CFG_Scale but perhaps just change to the most likely to replicate the prompt.
+ Make it look a lot better. I have incorporated styles but it still needs work and consistency.
+ Incorporate Gligen or Composable diffusion/latent couple. I might offer these as options at 512 x 512 right now.
+ Hook it up properly with Aubrushli itself and indeed with the StoryBoard Module.
+ Clean up code, I wasn't planning on a full app it just is increasingly going that way and right now spaghetti code and technical debt is increasing. I have created a sql boiler plate file which I will be updating and similarily I will look at the PYQT5 widgets etc that I repeat a lot. 

Anyway thats the initial readme, lots to add, watch this space. 
