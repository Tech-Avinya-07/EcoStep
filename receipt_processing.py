import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, ModelTypes
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxLLM
from database import Database
from databasetowordconverter import export_receipt_data_to_word
from datetime import datetime

db = Database('ocr_results.db')
def setup_watsonx():
    try:
        print("Setting up WatsonX...")
        credentials = Credentials(
            url="https://us-south.ml.cloud.ibm.com",
            api_key="add your api key here"
        )

        project_id = os.environ.get("PROJECT_ID", "add your project id here")

        model_id = ModelTypes.GRANITE_13B_CHAT_V2
        parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.STOP_SEQUENCES: ["Human:", "Receipt:", "Total"]
        }
        watsonx_llm = WatsonxLLM(
            model_id=model_id.value,
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params=parameters
        )
        print("WatsonX set up successfully.")
        return True, watsonx_llm
    except Exception as e:
        print(f"Error setting up WatsonX: {str(e)}")
        return False, f"Error setting up WatsonX: {str(e)}"

def process_receipt(receipt_text,conn, watsonx_llm):
    print("Processing receipt...")

    prompt_template = PromptTemplate(
        input_variables=["receipt"],
        template="""
Analyze the following receipt and perform these tasks:
1. Identify all purchased items (products) from the receipt.
2. For each identified item, calculate its carbon footprint in kg CO2e based on the quantity.
3. Classify each item into one of the following categories based on your knowledge:
   - Personal (groceries, food, and clothing)
   - Flight travel
   - Electricity
   - Vehicle (fuel, maintenance)

When calculating the carbon footprint:
- Use the first number after the identified product without a currency symbol as the weight/quantity.
- If only a cost per unit and total cost are given, calculate the quantity from that.
- Consider the nature of the item (e.g., dairy, meat, produce, packaged goods).
- Factor in typical production and transportation methods for this type of item.

Receipt:
{receipt}

Format your response as follows for each item, with no additional explanation:
Item Name: Carbon Footprint (kg CO2e) : Category
No need to return any calculations just return the final calculated carbon footprints for each of them.

Your response:
"""
    )

    # Create an LLMChain
    llm_chain = LLMChain(llm=watsonx_llm, prompt=prompt_template)

    # Run the LLM chain
    response = llm_chain.run(receipt=receipt_text)


    print("Receipt processing complete. Results:")
    words = response.split()  # Split the string into a list of words
    if len(words) > 1:
        words.pop()  # Remove the last word
        finalresult = ' '.join(words)
        return format_carbon_footprint(finalresult,conn)
 


def format_carbon_footprint(data,conn):
    # Initialize total footprint
    total_carbon_footprint = 0
    results = []
    # Split the data into lines
    lines = data.split('\n')
    
    # Iterate through each line
    for line in lines:
        # Split the line into multiple parts if there are multiple "Item Name" entries
        items = line.split("Item Name:")
        
        # Process each item, skipping the first part which might be empty
        for item in items[1:]:
            # Extract item name, carbon footprint, and category
            parts = item.split(':')
            if len(parts) >= 3:
                item_name = parts[0].strip()
                carbon_footprint_str = parts[1].strip().replace("kg CO2e", "").strip()
                category = parts[2].strip()
                
                # Convert to float and handle any possible errors
                try:
                    carbon_footprint = float(carbon_footprint_str)
                except ValueError:
                    print(f"Error converting carbon footprint for {item_name}: {carbon_footprint_str}")
                    continue
                current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Print formatted output
                print(f"Itemname : {item_name}- Carbon Footprint : {carbon_footprint:.3f} kg CO2e - Category: {category}")
                results.append({'item_name': item_name, 'carbon_footprint': carbon_footprint, 'category': category})
                db.insert_receipt_data(item_name, carbon_footprint, category,current_date)

                # Add to total carbon footprint
                total_carbon_footprint += carbon_footprint
    
    # Print total carbon footprint
    print(f"\nTotal Carbon Footprint: {total_carbon_footprint:.3f} kg CO2e")
    results.append({'Total Carbon Footprint of the receipt ' : total_carbon_footprint})

      # Fetch all receipts after insertion and append to Word document
    
    export_receipt_data_to_word(results, "receipt_carbon_footprint_chatbot.docx")

    return results
# Note: The main block has been removed as it's not needed in this module