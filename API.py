from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message
from utils import *

TOKENIZERS_PARALLELISM=True

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai.api_key)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question as truthfully as possible using only the provided context, 
and if the answer is not contained within the text below, say 'I don't know; if asked in Spanish, answer in Spanish""")

app = Flask(__name__)

# Define an API endpoint
@app.route('/api/your_endpoint', methods=['GET', 'POST'])
def your_endpoint():
        if request.method == 'GET':
        # Get the 'message' query parameter from the URL
            query = request.args.get('query')

            # Check if 'query' parameter is provided
            if query:
                human_msg_template = HumanMessagePromptTemplate.from_template(template="{query}")
                prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

                conversation_string = get_conversation_string()
                refined_query = query_refiner(conversation_string, query)
                context = find_match(refined_query)
                llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.1)
                conversation_text = context+"\n"+query
                response = llm.predict(conversation_text)
                
                response_data = {
                    "response": response,
                    "status": "GET request received with 'query'",
                }
                return jsonify(response_data), 200
            else:
                response_data = {
                    "error": "Missing 'message' parameter in the query",
                }
                return jsonify(response_data), 400
        
        elif request.method == 'POST':
            # Handle POST requests
            try:
                # Get JSON data from the request
                data = request.get_json()

                # Implement your logic using the data
                # Example: process data and return a response
                response_data = {
                    "message": "POST request received",
                    "data_received": data,
                }
                return jsonify(response_data), 200

            except Exception as e:
                # Handle errors gracefully
                return jsonify({"error": str(e)}), 400

    if __name__ == '__main__':
        app.run(debug=True)
