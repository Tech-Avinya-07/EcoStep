import os
import logging
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import cv2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextCleanerEnhance:
    NONE = 'none'
    NORMALIZE = 'normalize'
    STRETCH = 'stretch'

class TextCleanerLayout:
    PORTRAIT = 'portrait'
    LANDSCAPE = 'landscape'

class TextCleanerRotation:
    NONE = 'none'
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'

class TextCleanerCropOffset:
    """Handles cropping offsets for cleaning."""
    def __init__(self):
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.top = 0

    @property
    def is_set(self):
        return self.bottom != 0 or self.left != 0 or self.right != 0 or self.top != 0

    @property
    def is_valid(self):
        return self.bottom >= 0 and self.left >= 0 and self.right >= 0 and self.top >= 0

class TextCleanerScript:
    """Main class to perform text cleaning on images."""
    def __init__(self):
        self.adaptive_blur = 0.5
        self.background_color = 255  # Grayscale background color
        self.crop_offset = TextCleanerCropOffset()
        self.enhance_mode = TextCleanerEnhance.STRETCH
        self.filter_offset = 5
        self.filter_size = 3
        self.layout = TextCleanerLayout.PORTRAIT
        self.make_gray = True
        self.padding = 5
        self.rotation = TextCleanerRotation.NONE
        self.saturation = 100
        self.sharpen = 1.0
        self.smoothing_threshold = 50
        self.trim = True
        self.unrotate = True

    def execute(self, image_path):
        """Executes the text cleaning process on the input image."""
        if not os.path.exists(image_path):
            logging.error(f"Image file not found: {image_path}")
            return None

        image = Image.open(image_path)
        logging.info(f"Processing image: {image_path}")

        self.check_settings()

        # Apply various cleaning methods
        image = self.rotate_image(image)
        image = self.crop_image(image)
        image = self.convert_to_grayscale(image)
        image = self.enhance_image(image)
        image = self.reduce_noise(image)  # Enhanced noise reduction
        image = self.unrotate_image(image)  # Fine-tuned unrotation
        image = self.sharpen_image(image)
        image = self.saturate_image(image)
        image = self.adaptive_blur_image(image)
        image = self.dilate_image(image)  # Controlled dilation step
        image = self.trim_image(image)
        image = self.pad_image(image)

        # Save processed image
        # Save processed image, overwriting the original
        image.save(image_path)
        logging.info(f"Processed image overwritten: {image_path}")
        return image

    def check_settings(self):
        """Validates settings before processing."""
        if self.adaptive_blur < 0.0:
            raise ValueError("Invalid adaptive blur specified, value must be zero or higher.")
        if not self.crop_offset.is_valid:
            raise ValueError("Invalid crop offset specified, values must be zero or higher.")
        if self.filter_size < 0:
            raise ValueError("Invalid filter size specified, value must be zero or higher.")
        if self.padding < 0:
            raise ValueError("Invalid padding specified, value must be zero or higher.")
        if self.sharpen < 0.0:
            raise ValueError("Invalid sharpen specified, value must be zero or higher.")
        if self.smoothing_threshold is not None and (self.smoothing_threshold < 0 or self.smoothing_threshold > 100):
            raise ValueError("Invalid smoothing threshold specified, value must be between zero and 100.")

    def rotate_image(self, image):
        """Rotates the image based on layout and rotation settings."""
        if (self.layout == TextCleanerLayout.PORTRAIT and image.height < image.width) or \
           (self.layout == TextCleanerLayout.LANDSCAPE and image.height > image.width):
            if not self.is_text_aligned_correctly(np.array(image)):
                angle = -90 if self.rotation == TextCleanerRotation.COUNTERCLOCKWISE else 90
                image = image.rotate(angle, expand=True)
        return image

    def is_text_aligned_correctly(self, img_array):
        """Checks if the text is aligned correctly, especially for landscape images."""
        aspect_ratio = img_array.shape[1] / img_array.shape[0]
        if aspect_ratio > 1:  # Wide images are typically landscape
            return True
        return False

    def crop_image(self, image):
        """Crops the image based on specified offsets."""
        if not self.crop_offset.is_set:
            return image
        width, height = image.size
        left = self.crop_offset.left
        top = self.crop_offset.top
        right = width - self.crop_offset.right
        bottom = height - self.crop_offset.bottom
        return image.crop((left, top, right, bottom))

    def convert_to_grayscale(self, image):
        """Converts the image to grayscale if needed."""
        if self.make_gray:
            image = ImageOps.grayscale(image)
        return image

    def enhance_image(self, image):
        """Enhances the image brightness/contrast."""
        if self.enhance_mode == TextCleanerEnhance.STRETCH:
            return ImageOps.autocontrast(image)
        elif self.enhance_mode == TextCleanerEnhance.NORMALIZE:
            return ImageOps.equalize(image)
        return image

    def reduce_noise(self, image):
        """Enhanced noise reduction before dilation."""
        img_array = np.array(image)
        # Erode to reduce noise
        kernel = np.ones((2, 2), np.uint8)
        img_array = cv2.erode(img_array, kernel, iterations=1)
        # Apply Gaussian blur for further noise reduction
        img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
        # Use bilateral filter to preserve edges while reducing noise
        img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
        return Image.fromarray(img_array)

    def unrotate_image(self, image):
        """Deskews the image to correct slight rotations with better angle checks."""
        if self.unrotate:
            img_array = np.array(image)
            coords = np.column_stack(np.where(img_array < 128))
            angle = cv2.minAreaRect(coords)[-1]

            # Ensure angle is within reasonable range for deskewing
            if -10 <= angle <= 10:
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                (h, w) = img_array.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                img_array = cv2.warpAffine(img_array, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                logging.info(f"Corrected skew with angle: {angle:.2f} degrees")
            else:
                logging.info(f"Skipped unrotation due to unreasonable angle: {angle:.2f} degrees")
            
            return Image.fromarray(img_array)
        return image

    def sharpen_image(self, image):
        """Applies sharpening to the image."""
        if self.sharpen > 0.0:
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=100))
        return image

    def saturate_image(self, image):
        """Adjusts the image saturation correctly without altering color channels improperly."""
        img_array = np.array(image)
        if len(img_array.shape) == 2 or (img_array.shape[-1] == 1):
            logging.info("Skipping saturation adjustment; image is grayscale.")
            return image
        return image

    def adaptive_blur_image(self, image):
        """Applies adaptive blur to the image."""
        if self.adaptive_blur > 0.0:
            img_array = np.array(image)
            img_array = cv2.GaussianBlur(img_array, (3, 3), self.adaptive_blur)
            return Image.fromarray(img_array)
        return image

    def dilate_image(self, image):
        """Applies controlled dilation to enhance text readability."""
        img_array = np.array(image)
        # Use a smaller kernel and fewer iterations to reduce noise amplification
        kernel = np.ones((1, 2), np.uint8)  # Slightly smaller dilation kernel
        img_array = cv2.dilate(img_array, kernel, iterations=1)
        return Image.fromarray(img_array)

    def trim_image(self, image):
        """Trims the borders of the image if needed."""
        if self.trim:
            image = image.crop(image.getbbox())
        return image

    def pad_image(self, image):
        """Adds padding to the image with proper color handling."""
        if self.padding > 0:
            if image.mode == "L":
                image = ImageOps.expand(image, border=self.padding, fill=self.background_color)
            else:
                image = ImageOps.expand(image, border=self.padding, fill=(self.background_color,)*3)
        return image



