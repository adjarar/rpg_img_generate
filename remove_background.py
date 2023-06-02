import argparse
import os
from rembg import remove
from sd_api_tools import *
import discord
from PIL import Image

def remove_background(input_dir: str, output_dir: str, vebose=False):

    for img_file in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_file)

        if vebose:
            print(f"Removing background of: {img_path}")
        
        img = Image.open(img_path)
        img_bg_removed = remove(img)

        if vebose:
            print(f"Done removing background of: {img_path}")

        output_img_path = os.path.join(output_dir, img_file.replace(".png", "_without_bg.png"))
        img_bg_removed.save(output_img_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="remove background of the image")
    parser.add_argument("--input_dir", required=True, help="the input directory")
    parser.add_argument("--output_dir", required=True, help="the output directory")

    args = parser.parse_args()

    remove_background(args.input_dir, args.output_dir)

    webhook = discord.SyncWebhook.partial(1108891310351470662, '5Q-A_WqDX7Iiu6Y30oyifxGHdfL2PeErrW0MWA5kFjRTcGXbMv_Sv6NmtXhIwiOX0hf_')
    webhook.send('Finnished removing backgrounds', username='Background Remover')