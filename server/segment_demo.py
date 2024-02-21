import base64
import cv2
import warnings
import numpy as np
from PIL import Image
from io import BytesIO
import torch
from typing import List
from segment_anything import sam_model_registry, SamPredictor
from lang_sam import LangSAM
import matplotlib.pyplot as plt

def np_array_to_base64(array):
    return base64.b64encode(array).decode("utf-8")

def decode_base64_to_image(base64_str):
    """
    Decode a base64 string to a PIL Image object.
    """
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    return image

def base64_to_numpy(base64_str):
    """
    Convert a base64 string to a numpy array.
    """
    # Check for the presence of a base64 header
    if "base64" in base64_str:
        base64_str = base64_str.split(",")[1]
    pil_image = decode_base64_to_image(base64_str)
    return np.array(pil_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   



def segment_point(base64_image: str, point_coords: List):
    """
    Takes a base64 encoded image, a point (x, y coordinates).
    and returns the predicted masks.

    :param base64_image: Base64 encoded image string
    :param point_coords: Coordinates of the point as a numpy array [x, y]
    :return: Predicted masks
    """
    point_coords = np.array([point_coords])
    sam_checkpoint = "sam_vit_b_01ec64.pth"
    model_type = "vit_b"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)

    predictor = SamPredictor(sam)
    
    
    # Convert base64 image to numpy array
    image_np = base64_to_numpy(base64_image)
    
    # Ensure image is in RGB format if it's not already
    if image_np.shape[-1] == 4:  # Assuming the presence of an alpha channel
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2RGB)
    else:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    predictor.set_image(image_np)
    input_label = np.array([1])

    masks, scores, _ = predictor.predict(
        point_coords=point_coords,
        point_labels=input_label,
        multimask_output=True,
    )
   
    return masks.tolist(), scores.tolist()
    
def segment_text(base64_image, text_prompt):
    """
    Decodes a base64 encoded image, uses LangSAM model to predict masks, bounding boxes,
    phrases, and logits based on a text prompt, and optionally displays the results.

    :param base64_image: Base64 encoded image string.
    :param text_prompt: Text prompt for the LangSAM model.
    :return: masks, boxes, phrases, logits
    """
    # Decode the base64 string to a PIL Image
    image_pil = decode_base64_to_image(base64_image)
    
    # Initialize the LangSAM model
    model = LangSAM(sam_type='vit_b')
    
    # Predict masks, boxes, phrases, and logits using the model
    masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)
    
    # Convert masks to numpy arrays for easier handling
    masks_np = [mask.squeeze().cpu().numpy() for mask in masks]
    
    return masks_np, boxes
