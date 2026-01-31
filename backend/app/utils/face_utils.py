import base64
from pathlib import PosixPath

import cv2
import numpy as np
import torch


class FaceDetector:
    """
    A face detector based on OpenCV Haar cascades
    """

    def __init__(self):
        # Handle case where cv2.data is not available
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        except AttributeError:
            # Fallback if cv2.data is not available
            cascade_path = "haarcascade_frontalface_default.xml"

        # pylint: disable=no-member
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        # pylint: enable=no-member

    def detect_from_array(self, image_array):
        """
        Detect faces from a numpy array image
        """
        gray_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )
        # Return cropped face images
        return [image_array[y : y + h, x : x + w] for (x, y, w, h) in faces]


def detect_face(image):
    """
    Detect faces in an image using OpenCV Haar cascades.

    Args:
        image: Can be either a file path (str) or a numpy array representing an image

    Returns:
        List of numpy arrays representing detected faces, or empty list if no faces found
    """
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Handle different input types
    if isinstance(image, str):
        # If image is a file path
        image = cv2.imread(image, cv2.COLOR_BGR2RGB)
    elif isinstance(image, np.ndarray):
        # If image is already a numpy array
        pass
    else:
        raise ValueError("Image must be a file path string or numpy array")

    if image is None:
        return []

    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    # Return cropped face images
    return [image[y : y + h, x : x + w] for (x, y, w, h) in faces]


def image_to_base64(image):
    """
    Convert an image to base64 encoded string

    Args:
        image: Can be either a file path (str), numpy array, or bytes representing an image

    Returns:
        Base64 encoded string representation of the image
    """
    if isinstance(image, str):
        # Read image from file
        image_data = cv2.imread(image)
        _, buffer = cv2.imencode(".jpg", image_data)
        image_bytes = buffer.tobytes()
    elif isinstance(image, np.ndarray):
        # Convert numpy array to bytes
        _, buffer = cv2.imencode(".jpg", image)
        image_bytes = buffer.tobytes()
    elif isinstance(image, bytes):
        # Image is already bytes
        image_bytes = image
    else:
        raise ValueError("Image must be a file path string, numpy array, or bytes")

    # Encode bytes to base64
    base64_string = base64.b64encode(image_bytes).decode("utf-8")

    return base64_string


def base64_to_image(base64_string: str):
    """
    Convert a base64 encoded string to an image (numpy array)

    Args:
        base64_string: Base64 encoded string representing an image

    Returns:
        Numpy array representing the decoded image
    """
    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_string.encode("utf-8"))

    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # Decode numpy array to image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return image


@torch.no_grad()
def inference(net, img, device="cuda", to_array=True):
    use_cuda = device == "cuda"
    if img is None:
        img = np.random.randint(0, 255, size=(112, 112, 3), dtype=np.uint8)
    elif isinstance(img, str) or isinstance(img, PosixPath):
        img = cv2.imread(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (112, 112))
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0).float()
    img.div_(255).sub_(0.5).div_(0.5)
    # net.eval()
    # inference in amp mode
    img = img.to(device)
    net = net.to(device)
    feat = net(img, cuda=use_cuda)
    try:
        feat_c = feat.cpu()
        feat = feat_c
    except:
        pass
    if to_array:
        feat = feat.numpy()
    return feat
