import streamlit as st
import os
import tempfile
from ocr_main import OCRPipeline
import logging
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.title("OCR Pipeline with Receipt Analysis")

    st.write("Upload PDF or image files for OCR processing and receipt analysis.")

    # Upload PDF or image files
    uploaded_files = st.file_uploader("Choose PDF or image files", accept_multiple_files=True, type=['pdf', 'png', 'jpg', 'jpeg'])

    if uploaded_files:
        # Create temporary directory to save uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, 'input')
            os.makedirs(input_dir, exist_ok=True)

            # Define the hardcoded output directory
            output_dir = r"C:\OCR\EnhancedImage"
            os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

            # Save uploaded files to the temporary input directory
            for uploaded_file in uploaded_files:
                file_path = os.path.join(input_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

            # Initialize OCR pipeline with the input and output directories
            pipeline = OCRPipeline(input_dir, output_dir)

            # Process files when the button is clicked
            if st.button("Process Files"):
                with st.spinner("Processing files..."):
                    try:
                        # Run the OCR pipeline and capture the result
                        result = pipeline.run()  # This should return the list of dictionaries
                        st.success("OCR pipeline completed successfully!")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        result = None
                
                # Display the results if available
                st.subheader("Processing Results:")
                
                if result:
                    # Display the itemized results from the receipt analysis
                    st.write("Receipt Details:")
                    for entry in result:
                        # Check if the entry is for the total carbon footprint
                        if 'Total Carbon Footprint of the receipt ' in entry:
                            st.write(f"**Total Carbon Footprint:** {entry['Total Carbon Footprint of the receipt ']:.3f} kg CO₂e")
                        else:
                            # Display item details
                            st.write(f"**Item:** {entry.get('item_name', 'N/A')}")
                            st.write(f"**Carbon Footprint:** {entry.get('carbon_footprint', 0):.3f} kg CO₂e")
                            st.write(f"**Category:** {entry.get('category', 'Unknown')}")
                            st.write("---")  # Separator for readability
                else:
                    st.error("No valid result returned from the OCR pipeline.")
                
                
if __name__ == "__main__":
    main()
