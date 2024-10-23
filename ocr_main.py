import os
import logging
from pdf_processing import PDFProcessing
from image_preprocessing import ImagePreProcessing
from img_text_cleaning import TextCleanerScript
from ocr_processing import PerformingOCR
from receipt_processing import setup_watsonx, process_receipt
from database import Database
import time
from databasetowordconverter import export_receipt_data_to_word

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OCRPipeline:
    def __init__(self, input_dir, output_dir, db_path="ocr_results.db"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.db = Database('ocr_results.db')
        self.watsonx_llm = None

    def initialize(self):
        success, message = setup_watsonx()
        if success:
            self.watsonx_llm = message
            logging.info("WatsonX initialized successfully.")
        else:
            logging.error(f"Failed to initialize WatsonX: {message}")
            raise Exception("WatsonX initialization failed")

    def run(self):
        """
        Main method to run the full OCR pipeline.
        """
        logging.info("Starting the OCR pipeline...")
        
        # Initialize WatsonX
        self.initialize()

        # Step 1: Process PDFs and images
        logging.info("Processing files in the input directory...")
        PDFProcessing.convert_files(self.input_dir)

        # Verify that images were saved correctly
        image_files = [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith('_thresholded.jpg')]
        if not image_files:
            logging.error("No thresholded images found in the output directory after processing.")
            return  # Stop the pipeline if no images are found
        
        logging.info(f"Found {len(image_files)} images for OCR processing.")

        # Step 2: Preprocess each image
        logging.info("Preprocessing images...")
        for image_file in image_files:
            try:
                processed_image_path = ImagePreProcessing.enhance_image_quality(image_file)
                logging.info(f"Image enhancement completed for: {processed_image_path}")
            except Exception as e:
                logging.error(f"Error during image enhancement for {image_file}: {e}")
                continue

        # Step 3: Clean the text inside the images
        logging.info("Cleaning text inside images...")
        text_cleaner = TextCleanerScript()
        for image_file in image_files:
            cleaned_image = text_cleaner.execute(image_file)  # Clean the text in the image
            if cleaned_image:
                logging.info(f"Image text cleaned: {image_file}")

        # Step 4: Perform OCR on each cleaned image
        logging.info("Performing OCR...")
        ocr_processor = PerformingOCR()
        ocr_results = []
        for image_file in image_files:
            text_rows = ocr_processor.do_ocr(image_file)  # Perform OCR
            if text_rows:
                extracted_text = " ".join([row.word for row in text_rows])  # Join the words together
                logging.info(f"OCR completed for: {image_file}")
                print(f"Extracted text from {image_file}: {extracted_text}")

                receipt_result = process_receipt(extracted_text,self.db.conn, self.watsonx_llm)
                print(receipt_result)

        logging.info("OCR pipeline completed.")
        print("The program has been completed")
        return receipt_result

if __name__ == "__main__":
    # Define input and output directories
    input_dir = r"C:\Users\DURGA PRASAD\imgnew"
    output_dir = r"C:\OCR\EnhancedImage"

    # Initialize and run the OCR pipeline
    pipeline = OCRPipeline(input_dir, output_dir)
    pipeline.run()