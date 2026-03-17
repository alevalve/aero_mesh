import torch
import numpy as np
import cv2
from transformers import pipeline
from PIL import Image
from typing import List, Dict

class SAMSegmentation:
    """SAM adapted for 3D Depth Segmentation using Hugging Face Transformers"""

    def __init__(self, model_id: str = "facebook/sam-vit-base", device: str = None):
        if device is None:
            self.device_id = 0 if torch.cuda.is_available() else -1
        else:
            self.device_id = 0 if "cuda" in device else -1
            
        print(f"Initializing SAM pipeline with model: {model_id}")
        
        self.generator = pipeline(
            "mask-generation", 
            model=model_id, 
            device=self.device_id
        )

    def process_image(self, image_input) -> List[Dict]:
        """Processes an image and returns segmentation masks"""
        if isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            # Ensure it's a 3-channel image before converting color
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image_input)
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError("Invalid image input. Must be path, numpy array, or PIL Image.")
        
        return self.generator(image, points_per_batch=64)
    
    def get_corners(self, masks, click_x, click_y):
        """Finds the corners of the mask that contains the click point"""
        
        selected_mask = None
        min_area = float('inf')

        for mask_data in masks:
            binary_mask = np.array(mask_data['mask']) > 0
            h, w = binary_mask.shape

            # Boundary check
            if click_x < 0 or click_x >= w or click_y < 0 or click_y >= h:
                continue

            # If clicked pixel belongs to this mask
            if binary_mask[click_y, click_x]:
                area = np.sum(binary_mask)
                if area < min_area:
                    selected_mask = binary_mask
                    min_area = area
            
        if selected_mask is None:
            return None
        
        # Find contours of the selected mask
        mask_uint8 = (selected_mask * 255).astype(np.uint8)
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None
        
        cnt = max(contours, key=cv2.contourArea)

        # Approximate to a polygon 
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # If it forms a 4-sided shape
        if len(approx) == 4:
            approx = approx.squeeze()
            return [{"x": int(pt[0]), "y": int(pt[1])} for pt in approx]
        
        # Fallback to standard bounding box
        x, y, w, h = cv2.boundingRect(cnt)
        return [
            {"x": x, "y": y},         # Top-Left
            {"x": x + w, "y": y},     # Top-Right
            {"x": x + w, "y": y + h}, # Bottom-Right
            {"x": x, "y": y + h}      # Bottom-Left
        ]
