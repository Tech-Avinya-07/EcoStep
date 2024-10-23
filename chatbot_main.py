from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, ModelTypes
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxLLM
import docx

# Function to setup Watsonx
def setup_watsonx():
    try:
        credentials = Credentials(
            url="https://us-south.ml.cloud.ibm.com",
            api_key="add your api key here"  # Replace with your API key
        )
        
        project_id = "add your project id here"  # Replace with your project ID
        model_id = ModelTypes.GRANITE_13B_CHAT_V2
        
        parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 1000,
            GenParams.STOP_SEQUENCES: ["Question:", "Explanation:", "Answer:"]
        }
        
        watsonx_llm = WatsonxLLM(
            model_id=model_id.value,
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params=parameters
        )
        return watsonx_llm, "WatsonX set up successfully."
    except Exception as e:
        return None, f"Error setting up WatsonX: {str(e)}"

# Function to read the Word document
def read_word_document(file_path):
    """Reads the content from a Word document."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Function to process the question using the LLM
def process_question_with_doc(question, watsonx_llm, word_doc_path):
    try:
        # Read the Word document content
        document_content = read_word_document(word_doc_path)
        
        # Use WatsonX to analyze the question and the content of the Word document
        prompt_template = PromptTemplate(
            input_variables=["question", "document"],
            template="""You are an AI assistant named CarbonBuddy. Your task is to respond strictly based on the user's question. Only refer to the document content when it's relevant to answering the question. If the question does not require information from the document, respond using your own knowledge without unnecessary elaboration.

Do not answer unless a specific question is asked.
Keep answers concise and relevant to the topic.
Do not provide any additional information unless it directly relates to the question.

Question: {question}

Document content: {document}

Answer:"""
        )
        
        llm_chain = LLMChain(llm=watsonx_llm, prompt=prompt_template)
        response = llm_chain.run(question=question, document=document_content)
        
        return response.strip()
        
    except Exception as e:
        return f"Error processing question: {str(e)}"

if __name__ == "__main__":
    # Set up WatsonX
    watsonx_llm, msg = setup_watsonx()
    print(msg)

    # Example of processing a question using the Word document
    if watsonx_llm:
        question = "Can you calculate my total carbonfootprints?"
        word_doc_path = "report_carbon_footprint_chatbot.docx"  # Path to the Word document
        response = process_question_with_doc(question, watsonx_llm, word_doc_path)
        print(f"Response: {response}")
