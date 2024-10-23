import os
import logging
from paddleocr import PaddleOCR
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Row:
    def __init__(self, line, column, word_type, word):
        self.line = line
        self.column = column
        self.word_type = word_type
        self.word = word

class Identify:
    @staticmethod
    def string_type(text):
        """Identify the type of text (numeric, alphabetic, or mixed)."""
        text = str(text)  # Convert text to string
        if text.isdigit():
            return 1  # Numeric type
        elif text.isalpha():
            return 2  # Alphabetic type
        else:
            return 3  # Mixed type

class PerformingOCR:
    @staticmethod
    def do_ocr(image_dir):
        if not image_dir:
            logging.error("No image directory provided.")
            return None

        try:
            # Check if the file exists
            if not os.path.exists(image_dir):
                raise FileNotFoundError(f"Image file not found: {image_dir}")
            logging.info(f"Image file found: {image_dir}")

            # Check if the file is a valid image
            try:
                img = Image.open(image_dir)
                img.verify()  # Verify that it's a valid image
            except Exception as e:
                raise ValueError(f"Invalid image format or corrupt image: {image_dir}. Error: {e}")
            logging.info(f"Valid image format: {image_dir}")

            # Initialize PaddleOCR and perform OCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            result = ocr.ocr(image_dir, cls=True)
            logging.info(f"OCR processing completed for: {image_dir}")

            # Parse OCR results
            row_list = []
            line_num = 1

            for idx, res in enumerate(result):
                for word_info in res:  # word_info is a list of tuples [('recognized_text', confidence_score), ...]
                    word_text = word_info[1][0]  # Extract the recognized text
                    word_confidence = word_info[1][1]  # Confidence score

                    # Ensure word_confidence is a float before formatting
                    logging.info(f"Word: {word_text}, Confidence: {float(word_confidence):.2f}")

                    # Identify word type
                    type = Identify.string_type(word_text)

                    # Create Row object and set the type attribute
                    row = Row(line=line_num, column=1, word_type=type, word=word_text)
                    row.type = type  # Set the type attribute

                    # Append row to the list
                    row_list.append(row)

                line_num += 1

            logging.info(f"Total rows extracted: {len(row_list)}")
            return row_list

        except FileNotFoundError as e:
            logging.error(e)
        except ValueError as e:
            logging.error(e)
        except Exception as e:
            logging.error(f"Unexpected error during OCR processing: {e}")
            return None
