import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImagePreProcessing:
    @staticmethod
    def enhance_image_quality(image_directory):
        try:
            # Ensure the image file exists
            if not os.path.exists(image_directory):
                raise FileNotFoundError(f"Image file not found: {image_directory}")

            enhanced_image_dir = '/path/to/enhanced/images/'

            # Step 1: Load the image using OpenCV
            img = cv2.imread(image_directory)
            if img is None:
                raise ValueError(f"Failed to load image: {image_directory}")
            logging.info(f"Image loaded successfully: {image_directory}")

            # Step 2: Convert to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            logging.info("Converted to grayscale.")

            # Step 3: Adjust contrast (enhancing contrast after grayscale conversion)
            pil_img = Image.fromarray(gray_img)
            enhancer = ImageEnhance.Contrast(pil_img)
            contrast_img = enhancer.enhance(2)  # Increase contrast by a factor of 2
            contrast_img = np.array(contrast_img)
            logging.info("Contrast enhanced.")

            # Step 4: Noise removal using median blur
            denoised_img = cv2.medianBlur(contrast_img, 3)
            logging.info("Noise removed using median blur.")

            # Step 5: Detect skew angle and rotate
            skew_angle = ImagePreProcessing.detect_skew(denoised_img)
            if skew_angle:
                rotated_img = ImagePreProcessing.rotate_image(denoised_img, skew_angle)
                logging.info(f"Skew corrected with an angle of {skew_angle} degrees.")
            else:
                rotated_img = denoised_img
                logging.info("No skew detected.")

            # Step 6: Binarization (thresholding)
            _, binary_img = cv2.threshold(rotated_img, 127, 255, cv2.THRESH_BINARY)
            logging.info("Binarization (thresholding) applied.")

            # Step 7: Remove borders or trim white space
            trimmed_img = ImagePreProcessing.remove_borders(binary_img)
            logging.info("Borders removed.")

            # Step 8: Resize or set DPI equivalent (resize to simulate density)
            pil_img_final = Image.fromarray(trimmed_img)
            resized_img = pil_img_final.resize((int(pil_img_final.width * 2), int(pil_img_final.height * 2)))
            logging.info("Image resized to simulate DPI increase.")

            # Ensure the enhanced image directory exists
            if not os.path.exists(enhanced_image_dir):
                os.makedirs(enhanced_image_dir)

            # Save enhanced image
            enhanced_image_path = os.path.join(enhanced_image_dir, os.path.basename(image_directory))
            resized_img.save(enhanced_image_path)
            logging.info(f"Enhanced image saved to: {enhanced_image_path}")

        except FileNotFoundError as e:
            logging.error(e)
        except OSError as e:
            logging.error(f"Invalid image format for {image_directory}: {e}")
        except Exception as e:
            logging.error(f"Error during image enhancement: {e}")

    @staticmethod
    def detect_skew(image):
        try:
            # Use OpenCV's Hough transform to detect lines and estimate the skew angle
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

            if lines is not None:
                angle = np.mean([line[0][1] for line in lines])  # Extract the angle
                skew_angle = (angle * 180 / np.pi) - 90
                return skew_angle
            return 0  # No skew detected

        except Exception as e:
            logging.error(f"Error in skew detection: {e}")
            return 0

    @staticmethod
    def rotate_image(image, angle):
        try:
            # Get image dimensions
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)

            # Rotate the image by the detected skew angle
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated

        except Exception as e:
            logging.error(f"Error in rotating image: {e}")
            return image  # Return the original image if rotation fails

    @staticmethod
    def remove_borders(image):
        try:
            # Use OpenCV to find contours and crop the image
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                x, y, w, h = cv2.boundingRect(contours[0])
                cropped_img = image[y:y+h, x:x+w]
                return cropped_img
            return image  # Return original image if no contours are found

        except Exception as e:
            logging.error(f"Error in removing borders: {e}")
            return image  # Return the original image in case of failure
