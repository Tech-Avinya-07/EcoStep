from wand.image import Image as WandImage
from PIL import Image, ImageOps, ImageFilter
import os
import numpy as np

class PDFProcessing:

    @staticmethod
    def convert_files(directory):
        """
        Converts PDF files to images and processes image files by applying thresholding.
        """
        # Supported extensions
        pdf_ext = [".pdf"]
        img_ext = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]

        # Directory to save enhanced images
        output_dir = r"C:\OCR\EnhancedImage"
        os.makedirs(output_dir, exist_ok=True)

        # Fetch all files from the directory
        file_entries = [os.path.join(dp, f) for dp, dn, filenames in os.walk(directory)
                        for f in filenames if any(f.lower().endswith(e) for e in pdf_ext + img_ext)]

        for file_name in file_entries:
            print(f"Processing file '{file_name}'.")

            # Check if it's a PDF or an image
            if file_name.lower().endswith(tuple(pdf_ext)):
                # Process as PDF
                PDFProcessing.convert_pdf(file_name, output_dir)
            elif file_name.lower().endswith(tuple(img_ext)):
                # Process as image
                PDFProcessing.process_image(file_name, output_dir)

    @staticmethod
    def convert_pdf(pdf_file, output_dir):
        """
        Converts PDF pages to images and applies thresholding.
        """
        print(f"Converting PDF file '{pdf_file}'.")

        # Convert each page of the PDF to an image with 300 DPI
        with WandImage(filename=pdf_file, resolution=300) as pdf:
            for i, page in enumerate(pdf.sequence):
                with WandImage(page) as img:
                    img.format = 'jpeg'

                    # Convert image to numpy array for further processing
                    img_array = np.array(img)

                    # Apply Bradley Local Thresholding
                    thresholded_img_array = PDFProcessing.bradley_local_thresholding(img_array)

                    # Convert back to PIL image
                    thresholded_image = Image.fromarray(thresholded_img_array)

                    # Convert RGBA to RGB (JPEG doesn't support transparency)
                    if thresholded_image.mode == 'RGBA':
                        thresholded_image = thresholded_image.convert('RGB')

                    # Save the processed image
                    output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{i + 1}_thresholded.jpg")
                    thresholded_image.save(output_path)
                    print(f"Saved processed image: {output_path}")

    @staticmethod
    def process_image(image_file, output_dir):
        """
        Processes an image file by applying thresholding.
        """
        print(f"Processing image file '{image_file}'.")

        # Open the image and convert to numpy array
        img = Image.open(image_file)
        img_array = np.array(img)

        # Apply Bradley Local Thresholding
        thresholded_img_array = PDFProcessing.bradley_local_thresholding(img_array)

        # Convert back to PIL image
        thresholded_image = Image.fromarray(thresholded_img_array)

        # Save the processed image
        output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_file))[0]}_thresholded.jpg")
        thresholded_image.save(output_path)
        print(f"Saved processed image: {output_path}")

    @staticmethod
    def bradley_local_thresholding(image, window_size=15, threshold=0.15):
        """
        Perform Bradley Local Thresholding on the given image array.
        :param image: Grayscale image as a numpy array
        :param window_size: Size of the local window
        :param threshold: Fractional threshold
        :return: Thresholded image array
        """
        # Use ImageFilter.BoxBlur instead of ImageOps.box_blur
        mean_filter = Image.fromarray(image).filter(ImageFilter.BoxBlur(window_size // 2))
        mean_array = np.array(mean_filter)
        output_image = (image > (mean_array * (1.0 - threshold))).astype(np.uint8) * 255
        return output_image