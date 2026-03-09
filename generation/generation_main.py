import os
import requests
import argparse

from generation.meshy_client import (
    generate_3d_from_image,
    generate_3d_from_images
)


def single_image(image_path, api_key, output_dir):
    print("Running single-image 3D generation...")
    
    url = generate_3d_from_image(image_path, api_key)
    
    output_path = os.path.join(output_dir, "current_model.glb")
    
    download_model(url, output_path)

    return url


def multi_image(image_path, api_key, output_dir):
    print("Running multi-image 3D generation...")
    
    url = generate_3d_from_images(image_path, api_key)
    
    output_path = os.path.join(output_dir, "current_model.glb")
    
    download_model(url, output_path)

    return url

def call_3d_generation(images, api_key, output_dir, multiview=False):
    if multiview:
        generated_url = multi_image(images, api_key, output_dir)
    else:
        generated_url = single_image(images, api_key, output_dir)

    print("Mesh generated using Meshy")
    return generated_url 

def download_model(url, save_path):

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Download finished:", save_path)