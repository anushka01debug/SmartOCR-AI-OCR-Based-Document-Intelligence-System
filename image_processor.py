import cv2
import numpy as np
from PIL import Image
def pil_to_cv(pil_image):
    """Converts a PIL Image to a OpenCV BGR image."""
    # Convert RGB/RGBA to BGR
    open_cv_image = np.array(pil_image)
    if len(open_cv_image.shape) == 3:
        if open_cv_image.shape[2] == 4:  # RGBA
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGBA2BGR)
        else:  # RGB
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    else:
        # Grayscale image, duplicate channels to make BGR
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_GRAY2BGR)
    return open_cv_image
def cv_to_pil(cv_image):
    """Converts a OpenCV image (BGR or Gray) to a PIL Image."""
    if len(cv_image.shape) == 2:
        return Image.fromarray(cv_image)
    else:
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
def apply_grayscale(cv_img):
    """Converts image to grayscale."""
    if len(cv_img.shape) == 3:
        return cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    return cv_img
def apply_denoising(cv_img, strength=10):
    """Applies fastNlMeansDenoising or median filter to reduce noise."""
    # If colored
    if len(cv_img.shape) == 3:
        return cv2.fastNlMeansDenoisingColored(cv_img, None, strength, strength, 7, 21)
    else:
        return cv2.fastNlMeansDenoising(cv_img, None, strength, 7, 21)
def apply_contrast_enhancement(cv_img):
    """Enhances image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    # Requires grayscale image
    if len(cv_img.shape) == 3:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_img.copy()
        
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Return same dimensions as input
    if len(cv_img.shape) == 3:
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    return enhanced
def apply_binarization(cv_img, method="otsu"):
    """
    Applies binarization (black and white thresholding).
    Methods: 'otsu', 'adaptive_gaussian', 'adaptive_mean'
    """
    # Convert to grayscale first
    if len(cv_img.shape) == 3:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_img.copy()
        
    if method == "otsu":
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    elif method == "adaptive_gaussian":
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    elif method == "adaptive_mean":
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
        )
    else:
        # Default simple threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
    return thresh
def apply_deskew(cv_img):
    """
    Detects skew angle in text and rotates image to deskew it.
    Works by finding orientation of dark blobs of text.
    """
    # Copy input image
    working_img = cv_img.copy()
    
    # Convert to grayscale if color
    if len(working_img.shape) == 3:
        gray = cv2.cvtColor(working_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = working_img.copy()
        
    # Invert text: text needs to be white, background black for minAreaRect
    # First, let's threshold it using Otsu
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    # Find all coordinates of non-zero pixels (text pixels)
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return cv_img  # Return original if empty
        
    # Compute the minimum bounding rectangle of all non-zero pixels
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    
    # OpenCV minAreaRect returns angle in range [-90, 0)
    # The behavior changed in OpenCV 4.5+ where angle is in [0, 90]
    # Let's write a robust parser for the angle:
    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = 90 - angle
    else:
        angle = -angle
        
    # Ignore extremely small rotations to save computation and prevent blurring
    if abs(angle) < 0.5 or abs(angle) > 45:
        return cv_img
        
    # Calculate rotation matrix and rotate
    (h, w) = cv_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    
    return rotated
def apply_upscaling(cv_img, scale_factor=2):
    """Upscales image using cubic interpolation. Useful for small text."""
    if scale_factor == 1:
        return cv_img
    h, w = cv_img.shape[:2]
    new_h, new_w = int(h * scale_factor), int(w * scale_factor)
    return cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
def run_preprocessing_pipeline(pil_img, options):
    """
    Executes a sequence of image processing steps based on active options dictionary.
    Example options:
    {
        'upscale': True,
        'upscale_factor': 2,
        'denoise': False,
        'denoise_strength': 10,
        'contrast': True,
        'grayscale': True,
        'deskew': True,
        'binarize': True,
        'binarize_method': 'otsu'
    }
    """
    # Convert to OpenCV format
    cv_img = pil_to_cv(pil_img)
    
    # 1. Upscaling first to preserve details
    if options.get('upscale', False):
        factor = options.get('upscale_factor', 2)
        cv_img = apply_upscaling(cv_img, factor)
        
    # 2. Denoising
    if options.get('denoise', False):
        strength = options.get('denoise_strength', 10)
        cv_img = apply_denoising(cv_img, strength)
        
    # 3. Deskewing (should be done on high quality, prior to binarization)
    if options.get('deskew', False):
        cv_img = apply_deskew(cv_img)
        
    # 4. Contrast enhancement
    if options.get('contrast', False):
        cv_img = apply_contrast_enhancement(cv_img)
        
    # 5. Grayscale
    if options.get('grayscale', False):
        cv_img = apply_grayscale(cv_img)
        
    # 6. Binarization (always returns grayscale/binary)
    if options.get('binarize', False):
        method = options.get('binarize_method', 'otsu')
        cv_img = apply_binarization(cv_img, method)
        
    # Convert back to PIL
    return cv_to_pil(cv_img)
