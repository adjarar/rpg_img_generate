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
parser.add_argument('--destroy_pod', action='store_true', help='Destroy the pod when the script finshed executing')
parser.add_argument("--upload", action="store_true", help="upload the outputs to fileio")
parser.add_argument("--output_dir_path", type=str, default=os.path.join(os.getcwd(), "output"), help="Output directory path")

args = parser.parse_args()


# for each prompt itterate over the following in the folder of prompts
while len(os.listdir(prompts_dir)) > 0:

    prompt_path = os.path.join(prompts_dir, os.listdir(prompts_dir)[0])
    
    # loads the json prompts
    with open(prompt_path, 'r') as prompts_file:
        prompts_file = json.load(prompts_file)

    # put the json elements in a variable
    prompts_name = prompts_file["name"]
    prompts = prompts_file["prompts"]

    with_bg_dir_name = "_".join([prompts_name, "with_bg"])
    without_bg_dir_name = "_".join([prompts_name, "without_bg"])

    with_bg_dir_path = os.path.join(args.output_dir_path, with_bg_dir_name)
    without_bg_dir_path = os.path.join(args.output_dir_path, without_bg_dir_name)
    processed_prompts_dir_path = os.path.join(os.getcwd(), "processed_prompts")

    os.makedirs(with_bg_dir_path)
    os.makedirs(without_bg_dir_path)
    os.makedirs(processed_prompts_dir_path)

    # loads the correct model
    requests.post(url=f'{args.sd_url}/sdapi/v1/options', json={"sd_model_checkpoint": "fantassifiedIcons_fantassifiedIconsV20.safetensors [8340e74c3e]"})

    # generate images
    txt2img_batch_generate(args.sd_url, prompts, with_bg_dir_path, prompts_name, args.steps, args.batch_size, args.iterations)

    # zip and upload the folder
    if args.upload:
        shutil.make_archive(with_bg_dir_path, 'zip', with_bg_dir_path)
        file_url = upload_to_fileio(with_bg_dir_path + ".zip")
        webhook.send(f'Finished generating {prompts_name} images. Download: {file_url}', username='Image Generator')

    remove_background(with_bg_dir_path, without_bg_dir_path)

    # zip and upload bg images
    if args.upload:
        shutil.make_archive(without_bg_dir_path, 'zip', without_bg_dir_path)
        file_url = upload_to_fileio(without_bg_dir_path + ".zip")
        webhook.send(f'Finished generating {prompts_name} no bg images. Download: {file_url}', username='Image Generator')
    
    # move the prompt to the processed folder
    shutil.move(prompt_path, processed_prompts_dir_path)

# send final finished message
webhook.send("Finished generating images and removing backgrounds", username="Finished All Jobs")

if args.destroy_pod:
    os.system("./vast stop instance ${VAST_CONTAINERLABEL:2}")