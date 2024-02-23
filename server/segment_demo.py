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
from utils import np_array_to_base64, decode_base64_to_image, base64_to_numpy

# Initialize the LangSAM model
model = LangSAM(sam_type="vit_b")
sam_checkpoint = "sam_vit_b_01ec64.pth"
model_type = "vit_b"

device = "cuda" if torch.cuda.is_available() else "cpu"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)


def segment_point(base64_image: str, point_coords: List):
    """
    Takes a base64 encoded image, a point (x, y coordinates).
    and returns the predicted masks.

    :param base64_image: Base64 encoded image string
    :param point_coords: Coordinates of the point as a numpy array [x, y]
    :return: Predicted masks
    """
    point_coords = np.array([point_coords])

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

    best_mask = None
    best_score = 0
    for i, (mask, score) in enumerate(zip(masks, scores)):
        if score > best_score:
            best_mask = mask
            best_score = score
    # Resize best_mask to be 1/2 the size of the original image
    best_mask = np.uint8(best_mask * 255)
    # Convert best mask to image then base64
    best_mask = Image.fromarray(best_mask)
    buffered = BytesIO()
    best_mask.save(buffered, format="JPEG")
    best_mask = base64.b64encode(buffered.getvalue())
    best_mask = best_mask.decode("utf-8")
    return best_mask, best_score


def segment_text(base64_image, text_prompt):
    """
    Decodes a base64 encoded image, uses LangSAM model to predict masks, bounding boxes,
    phrases, and logits based on a text prompt, and optionally displays the results.

    :param base64_image: Base64 encoded image string.
    :param text_prompt: Text prompt for the LangSAM model.
    :return: masks, boxes, phrases, logits
    """
    # Convert base64 image to numpy array
    image_np = base64_to_numpy(base64_image)
    image_pil = Image.fromarray(image_np)

    # Predict masks, boxes, phrases, and logits using the model
    masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)

    # Convert masks to numpy arrays for easier handling
    masks_np = [mask.squeeze().cpu().numpy() for mask in masks]

    mask = masks_np[0]
    box = boxes[0]

    # Convert mask to image then base64
    mask = np.uint8(mask * 255)
    mask = Image.fromarray(mask)
    buffered = BytesIO()
    mask.save(buffered, format="JPEG")
    mask = base64.b64encode(buffered.getvalue())
    mask = mask.decode("utf-8")

    # Convert box tensor to list
    box = box.tolist()

    return mask, box
