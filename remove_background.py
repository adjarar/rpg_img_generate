import argparse
import os
from rembg import remove
from sd_api_tools import *
import discord
from PIL import Image

def remove_background(input_dir: str, output_dir: str, vebose=False):

    images = os.listdir(input_dir)

    for i, img_file in enumerate(images):
        img_path = os.path.join(input_dir, img_file)

        img = Image.open(img_path)
        img_bg_removed = remove(img)

        
        output_img_path = os.path.join(output_dir, img_file.replace(".png", "_without_bg.png"))
        img_bg_removed.save(output_img_path)

        if vebose:
            print(f"Done removing background and saving of: {img_path} ( {i} / {images})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="remove background of the image")
    parser.add_argument("--input_dir", required=True, help="the input directory")
    parser.add_argument("--output_dir", required=True, help="the output directory")
    parser.add_argument("--verbose", action="store_true", default=False)

    args = parser.parse_args()

    remove_background(args.input_dir, args.output_dir, args.verbose)

    webhook = discord.SyncWebhook.partial(1108891310351470662, '5Q-A_WqDX7Iiu6Y30oyifxGHdfL2PeErrW0MWA5kFjRTcGXbMv_Sv6NmtXhIwiOX0hf_')
    webhook.send('Finnished removing backgrounds', username='Background Remover')