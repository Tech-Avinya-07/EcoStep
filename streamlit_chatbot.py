import streamlit as st
from chatbot_main import setup_watsonx, process_question_with_doc, read_word_document

def main():
    st.title("CarbonBuddy: Carbon Footprint QA System")
    
    # Path to the Word document
    word_doc_path = "receipt_carbon_footprint.docx"  # Make sure to adjust this path if needed
    
    # Automated initialization
    if 'system_initialized' not in st.session_state:
        with st.spinner("Initializing CarbonBuddy..."):
            watsonx_llm, message = setup_watsonx()  # Get LLM and message
            if watsonx_llm:
                st.session_state['system_initialized'] = True
                st.session_state['watsonx_llm'] = watsonx_llm  # Save LLM in session state
                st.success(message)
            else:
                st.error(message)
                st.stop()  # Stop the app if initialization fails

    # Main chat interface
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Display chat messages
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input for user prompt
    if prompt := st.chat_input("Ask about carbon emissions or the report"):
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use the saved LLM and process the question
                    response = process_question_with_doc(prompt, st.session_state['watsonx_llm'], word_doc_path)
                    st.markdown(f"**Bot:** {response}")
                    st.session_state['messages'].append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try rephrasing your question or try again later.")

if __name__ == "__main__":
    main()
