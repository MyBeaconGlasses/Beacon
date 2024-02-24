import base64
import cv2
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

def calculate_padded_bbox(mask_np, padding_percent=10):
    """
    Calculate the bounding box of the mask and add padding.
    :param mask_np: Numpy array of the mask.
    :param padding_percent: Percentage of padding to add to each side.
    :return: A tuple representing the padded bounding box (x_min, y_min, x_max, y_max).
    """
    rows = np.any(mask_np, axis=1)
    cols = np.any(mask_np, axis=0)
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    # Calculate padding
    height, width = mask_np.shape[:2]
    x_pad = int((x_max - x_min) * padding_percent / 100)
    y_pad = int((y_max - y_min) * padding_percent / 100)

    # Apply padding without going over the edge
    x_min = max(x_min - x_pad, 0)
    y_min = max(y_min - y_pad, 0)
    x_max = min(x_max + x_pad, width - 1)
    y_max = min(y_max + y_pad, height - 1)

    return x_min, y_min, x_max, y_max

def add_padding_and_display(image, box, padding_ratio=0.1):
    """
    Adds a specified percentage of padding to the bounding box, crops the image to this padded box,
    and displays the cropped image. Ensures padding does not extend beyond image bounds.

    :param image: The image as a PIL Image or numpy array.
    :param box: The bounding box as a tuple (x_min, y_min, x_max, y_max).
    :param padding_ratio: The ratio of padding to add to each side of the box (default is 10% or 0.1).
    
    :return: The cropped image as a PIL Image.
    """
    # Determine image dimensions
    if isinstance(image, Image.Image):
        width, height = image.size
    elif isinstance(image, np.ndarray):
        height, width, _ = image.shape
        image = Image.fromarray(image)
    else:
        raise ValueError("Image must be a PIL Image or numpy array.")

    # Unpack the bounding box and calculate padding
    x_min, y_min, x_max, y_max = box
    pad_width = (x_max - x_min) * padding_ratio
    pad_height = (y_max - y_min) * padding_ratio

    # Apply padding, ensuring coordinates remain within image bounds
    x_min_padded = max(0, int(x_min - pad_width))
    y_min_padded = max(0, int(y_min - pad_height))
    x_max_padded = min(width, int(x_max + pad_width))
    y_max_padded = min(height, int(y_max + pad_height))

    # Crop and display the image
    cropped_image = image.crop((x_min_padded, y_min_padded, x_max_padded, y_max_padded))
    
    # Convert to base64
    buffered = BytesIO()
    # Save as temp file
    cropped_image.save(buffered, format="JPEG")
    cropped_image = base64.b64encode(buffered.getvalue())
    cropped_image = cropped_image.decode("utf-8")
    
    
    return cropped_image

def crop_image_from_mask(image, mask):
    # Convert the mask to uint8 format
    mask_uint8 = (mask * 255).astype(np.uint8)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Image dimensions
    img_height, img_width = image.shape[:2]

    for contour in contours:
        # Compute the bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate padding (10% of the bounding box size)
        pad_w = int(0.1 * w)
        pad_h = int(0.1 * h)
        
        # Apply padding to the bounding box coordinates
        # Make sure the coordinates do not go out of image bounds
        x_pad = max(x - pad_w, 0)
        y_pad = max(y - pad_h, 0)
        w_pad = w + 2 * pad_w
        h_pad = h + 2 * pad_h
        
        # Adjust width and height to not exceed image bounds
        if x_pad + w_pad > img_width:
            w_pad = img_width - x_pad
        if y_pad + h_pad > img_height:
            h_pad = img_height - y_pad
        
        # Extract the padded area
        extracted_image_with_padding = image[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
        
        # Convert to base64
        buffered = BytesIO()
        extracted_image_with_padding = Image.fromarray(extracted_image_with_padding)
        extracted_image_with_padding.save(buffered, format="JPEG")
        extracted_image_with_padding = base64.b64encode(buffered.getvalue())
        extracted_image_with_padding = extracted_image_with_padding.decode("utf-8")
        
        return extracted_image_with_padding

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
    best_mask = np.uint8(best_mask * 255)
    
    image = crop_image_from_mask(image_np, best_mask)

    
    
    # Convert best mask to image then base64
    best_mask = Image.fromarray(best_mask)
    buffered = BytesIO()
    best_mask.save(buffered, format="JPEG")
    best_mask = base64.b64encode(buffered.getvalue())
    best_mask = best_mask.decode("utf-8")
    

    return best_mask, best_score, image


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
    
    image = add_padding_and_display(image_np, boxes[0])

    return mask, box, image
