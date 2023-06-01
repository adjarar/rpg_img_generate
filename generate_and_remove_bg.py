import discord
import requests
import argparse
import os
import json
import shutil
from upload_to_fileio import upload_to_fileio
from txt2img_batch_generate import txt2img_batch_generate
from remove_background import remove_background

webhook = discord.SyncWebhook.partial(1108891310351470662, '5Q-A_WqDX7Iiu6Y30oyifxGHdfL2PeErrW0MWA5kFjRTcGXbMv_Sv6NmtXhIwiOX0hf_')
prompts_dir = os.path.join(os.getcwd(), 'prompts')

parser = argparse.ArgumentParser(description="txt2img script")
parser.add_argument("--sd_url", type=str, default="http://localhost:7860", help="Stable Diffusion URL")
parser.add_argument("--steps", type=int, default=5, help="Number of steps")
parser.add_argument("--batch_size", type=int, default=1, help="Batch size")
parser.add_argument("--iterations", type=int, default=1, help="Number of iterations")
parser.add_argument('--destroy_pod_when_finished', action='store_true', help='Destroy the pod when the script finshed executing')

args = parser.parse_args()


# for each prompt itterate over the following in the folder of prompts
for prompt_name in os.listdir(prompts_dir):

    prompt_path = os.path.join(prompts_dir, prompt_name)
    
    # loads the json prompts
    with open(prompt_path, 'r') as prompts_file:
        prompts_file = json.load(prompts_file)

    # put the json elements in a variable
    prompts_name = prompts_file["name"]
    prompts = prompts_file["prompts"]

    with_bg_dir_name = "_".join([prompts_name, "with_bg"])
    without_bg_dir_name = "_".join([prompts_name, "without_bg"])

    with_bg_dir_path = os.path.join(os.getcwd(), with_bg_dir_name)
    without_bg_dir_path = os.path.join(os.getcwd(), without_bg_dir_name)

    os.makedirs(with_bg_dir_path)
    os.makedirs(without_bg_dir_path)

    # loads the correct model
    requests.post(url=f'{args.sd_url}/sdapi/v1/options', json={"sd_model_checkpoint": "fantassifiedIcons_fantassifiedIconsV20.safetensors [8340e74c3e]"})

    # generate images
    txt2img_batch_generate(args.sd_url, prompts, with_bg_dir_path, prompts_name, args.steps, args.batch_size, args.iterations)

    # zip the folder
    shutil.make_archive(with_bg_dir_path, 'zip', with_bg_dir_path)

    # upload to file.io and get the download link
    file_url = upload_to_fileio(with_bg_dir_path + ".zip")

    # post the link to discord
    webhook.send(f'Finished generating {prompts_name} images. Download: {file_url}', username='Image Generator')

    # remove bg
    remove_background(with_bg_dir_path, without_bg_dir_path)

    # zip bg images
    shutil.make_archive(without_bg_dir_path, 'zip', without_bg_dir_path)

    # upload bg zip to file.io
    file_url = upload_to_fileio(without_bg_dir_path + ".zip")
    webhook.send(f'Finished generating {prompts_name} no bg images. Download: {file_url}', username='Image Generator')

# send final finished message
webhook.send("Finished generating images and removing backgrounds", username="Finished All Jobs")

if args.destroy_pod_when_finished:
    os.system("./vast stop instance ${VAST_CONTAINERLABEL:2}")