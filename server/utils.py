import base64
from PIL import Image
from io import BytesIO


def np_array_to_base64(array):
    """
    Convert a numpy array to a base64 string.
    """
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
