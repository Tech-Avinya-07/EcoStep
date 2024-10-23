
# EcoStep

### Project Overview
EcoStep allows users to assess the carbon footprint of their purchases by analyzing receipts using OCR and IBM WatsonX. The system categorizes items, provides carbon footprint insights, and generates detailed reports. It also integrates a chatbot that answers user queries based on the stored data, considering their carbon footprint information from the database.

---

### Features
- **Receipt Analysis**: Extract and analyze data from receipts to compute carbon footprints.
- **OCR Integration**: Processes PDF and image receipts using advanced OCR techniques.
- **Category Classification**: Items are categorized into Personal, Flight Travel, Electricity, and Vehicle.
- **Personalized Recommendations**: Offers suggestions to reduce carbon emissions based on user purchase history.
- **Data Storage and Retrieval**: Uses SQLite to store and query receipts for historical analysis.
- **Graphical Reports**: Generates pie and bar charts representing carbon emissions over time and by category.
- **WatsonX Integration**: Utilizes IBM WatsonX for chatbot interaction, receipt analysis, and report generation.

---

### Installation

#### Prerequisites
- Python 3.8+
- pip (Python package manager)

#### Steps to Install:
1. Clone the repository:
    ```bash
    https://github.com/Tech-Avinya-07/EcoStep.git
    cd EcoStep
    ```

2. Install the required dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

3. Update WatsonX credentials in the relevant files (`chatbot_main.py`, `receipt_processing.py`, `report_generator.py`) by replacing the API key and project ID.

4. Initialize the SQLite database:
    - The SQLite database (`ocr_results.db`) is generated automatically upon running the application.

---

### Usage

1. Launch the chatbot interface using Streamlit:
    ```bash
    streamlit run streamlit_chatbot.py
    ```
    You can interact with the chatbot, ask questions about your carbon footprint, and receive personalized insights.

2. To process receipts (PDFs/images), run the OCR pipeline:
    ```bash
    streamlit run  streamlit_ocr.py
    ```
    Upload your receipt, and the system will extract, analyze, and display your carbon footprint.

3. To geenrate the report, run the report_generator.py file:
   ```bash
    python report_generator.py
    ```
   The report will be saved to report_carbon_footprint_user.docx .You can open it to see your personalised report.
---

### Modules Overview

The project consists of 12 key Python scripts:
1. **`chatbot_main.py`**: Sets up IBM WatsonX and processes user queries using the WatsonX LLM for natural language understanding and receipt analysis.
2. **`database.py`**: Manages SQLite database operations, including storing and querying receipt data.
3. **`databasetowordconverter.py`**: Converts receipt data from the SQLite database into Word documents.
4. **`image_preprocessing.py`**: Preprocesses images to enhance quality and prepare them for OCR.
5. **`img_text_cleaning.py`**: Cleans and enhances text from images for better OCR accuracy.
6. **`ocr_main.py`**: Coordinates the OCR pipeline, processes images, and interacts with the database.
7. **`ocr_processing.py`**: Implements OCR using PaddleOCR to extract text from receipts.
8. **`pdf_processing.py`**: Converts PDFs to images and applies image thresholding for better text extraction.
9. **`receipt_processing.py`**: Processes receipt text, calculates carbon footprints, and categorizes items using WatsonX.
10. **`report_generator.py`**: Generates detailed carbon footprint reports, including category-wise and date-wise analysis. Graphical visualizations are also generated, and personalized suggestions are provided by WatsonX.
11. **`streamlit_chatbot.py`**: Provides the Streamlit interface for interacting with the CarbonBuddy chatbot.
12. **`streamlit_ocr.py`**: Provides the Streamlit interface for users to upload and process receipts through the OCR pipeline.

---

### WatsonX Integration Details

IBM WatsonX is a key component in both the **receipt analysis**, **chatbot**, and **report generation** functionalities.

#### WatsonX AI in Receipt Analysis
When a receipt is processed, WatsonX is used to analyze the extracted text. It categorizes items, calculates their carbon footprint based on type and quantity, and stores this data in the SQLite database.

#### WatsonX AI in the Chatbot
WatsonX powers the chatbot that interacts with users, answering their queries about carbon footprints. It uses natural language processing to understand the user’s questions and responds based on the stored data.

#### WatsonX AI in Report Generation
WatsonX analyzes the generated report and provides customized recommendations for reducing carbon emissions. These suggestions are based on the carbon footprint trends from a user’s purchases, offering actionable advice tailored to their shopping patterns.

---

### Working Demo

https://drive.google.com/file/d/1iO_HiZ7Lrp1Z1DYt7qoTsk0HaTWWUF_n/view?usp=drive_link

---

### Contribution

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

### License

This project is licensed under the MIT License.

