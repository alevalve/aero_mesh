import threading
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import math

M_TO_FT = 3.28084
M_TO_IN = 39.3701
M2_TO_FT2 = 10.7639

def conversion(distance, metric):
    if metric == "inches":   return distance * M_TO_IN
    if metric == "feet":     return distance * M_TO_FT
    if metric == "meters":   return distance
    if metric == "area_ft2": return distance * M2_TO_FT2
    return distance

class DepthEstimator:
    def __init__(self, model_id="depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf"):
        self.device = "cpu"
        # Added use_fast=False to silence the deprecation warning
        self.processor = AutoImageProcessor.from_pretrained(model_id, use_fast=False)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_id).to(self.device)
        self.model.eval()

        self._lock = threading.Lock()
        self._depth_map = None
        self._focal_px = None

    def update_frame(self, rgb_frame):
        # Run inference synchronously on the main thread
        h, w = rgb_frame.shape[:2]
        inputs = self.processor(images=Image.fromarray(rgb_frame), return_tensors="pt").to(self.device)

        with torch.inference_mode():
            prediction = torch.nn.functional.interpolate(
                self.model(**inputs).predicted_depth.unsqueeze(1),
                size=(h, w), mode="bicubic", align_corners=False,
            ).squeeze()

        with self._lock:
            self._depth_map = prediction.cpu().numpy()
            self._focal_px = get_focal_length_px(w)

    def get_3d_point(self, x, y, depth_map, focal_px):
        h, w = depth_map.shape
        depth = depth_map[int(y), int(x)]
        return np.array([
            (x - w / 2) * depth / focal_px,
            (y - h / 2) * depth / focal_px,
            depth
        ])

    def metrics_from_touches(self, touches, display_w, display_h):
        with self._lock:
            if self._depth_map is None:
                return {"error": "Depth map not ready"}
            depth_map, focal_px = self._depth_map, self._focal_px

        dh, dw = depth_map.shape
        pts = [self.get_3d_point(
            t["x"] * dw / display_w,
            t["y"] * dh / display_h,
            depth_map, focal_px
        ) for t in touches]

        if len(pts) == 2:
            dist = float(np.linalg.norm(pts[0] - pts[1]))
            return {
                "meters":  conversion(dist, "meters"),
                "feet":    conversion(dist, "feet"),
                "inches":  conversion(dist, "inches"),
            }

        if len(pts) == 4:
            def tri(a, b, c): return 0.5 * np.linalg.norm(np.cross(b - a, c - a))
            area = float(tri(pts[0], pts[1], pts[2]) + tri(pts[0], pts[2], pts[3]))
            return {
                "area_m2":   conversion(area, "meters"),
                "area_ft2":  conversion(area, "area_ft2"),
            }

        return {"error": "Need 2 or 4 points"}
    
def get_focal_length_px(frame_w, fov_degrees=70):
    return (frame_w / 2) / math.tan(math.radians(fov_degrees / 2))