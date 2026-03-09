import requests
import base64
import time
import os
from io import BytesIO
from PIL import Image
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = os.getenv("MESHY_API_KEY")

BASE_URL_SINGLE = "https://api.meshy.ai/openapi/v1/image-to-3d"
BASE_URL_MULTI = "https://api.meshy.ai/openapi/v1/multi-image-to-3d"


def encode_image(image_path):

    img = Image.open(image_path)
    img = img.convert("RGB")
    img.thumbnail((512, 512))

    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=85)

    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{base64_data}"


def poll_task(status_url, headers):

    while True:

        status_res = requests.get(status_url, headers=headers, verify=False)
        data = status_res.json()

        status = data.get("status")
        progress = data.get("progress", 0)

        if status == "SUCCEEDED":
            print("\nGeneration Complete")
            return data.get("model_urls", {}).get("glb")

        elif status == "FAILED":
            raise RuntimeError(data.get("task_error"))

        else:
            print(f"Status: {status} | Progress: {progress}%", end="\r")
            time.sleep(5)


# SINGLE IMAGE PIPELINE

def generate_3d_from_image(image_path, api_key):

    headers = {"Authorization": f"Bearer {api_key}"}

    encoded = encode_image(image_path)

    payload = {
        "image_url": encoded,
        "enable_pbr": False,
        "should_remesh": False,
        "lowpoly": True,
    }

    response = requests.post(BASE_URL_SINGLE, headers=headers, json=payload)
    response.raise_for_status()

    task_id = response.json()["result"]

    status_url = f"{BASE_URL_SINGLE}/{task_id}"

    return poll_task(status_url, headers)


# MULTI IMAGE PIPELINE

def generate_3d_from_images(image_paths, api_key):

    headers = {"Authorization": f"Bearer {api_key}"}

    encoded_images = [encode_image(p) for p in image_paths]

    payload = {
        "image_urls": encoded_images,
        "enable_pbr": True,
        "should_remesh": True,
        "should_texture": True,
    }

    response = requests.post(BASE_URL_MULTI, headers=headers, json=payload)
    response.raise_for_status()

    task_id = response.json()["result"]

    status_url = f"{BASE_URL_MULTI}/{task_id}"

    return poll_task(status_url, headers)

