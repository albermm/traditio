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
@app.route('/api/consultatio', methods=['GET'])
def consultatio():
        chat_history = []
        if request.method == 'GET':
        # Get the 'message' query parameter from the URL
            query = request.args.get('query')
            
            print(f"Received query: {query}")

            # Check if 'query' parameter is provided
            if query:
                human_msg_template = HumanMessagePromptTemplate.from_template(template="{query}")
                prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

                conversation_string = [
                                        "Human: Hey, I've been reading about serious sin, and I'm wondering how often I should confess to foster the cleanliness of my soul.",
                                        "Bot: Hi there! Confessing regularly can indeed help maintain the beauty of your soul and help you grow. Would you like to know more about the benefits of regular confession?",
                                        "Human: Yes, please! I'd also like to understand the role of history and sin's power in all of this.",
                                        "Bot: Of course! Regular confession helps us acknowledge our mistakes and seek forgiveness. History shows us that the power of sin can be a daunting force, but by confessing regularly, we can strive to overcome it and mature in life.",
                                        "Human: That makes sense. So, how should I approach confession? Any specific guidance?",
                                        "Bot: Absolutely. When you confess, approach it with sincerity and a desire for personal growth. Reflect on your actions and intentions, and seek guidance from a trusted spiritual advisor for a fulfilling confession experience.",
                                        "Human: Thanks for the advice. One last thing, could you help me come up with a relevant question to deepen my understanding of this topic?",
                                        "Bot: Sure thing! How about this: 'What are some historical examples that highlight the impact of regular confession in fostering spiritual growth and overcoming the power of sin?'"
                                    ]

                refined_query = query_refiner(conversation_string, query)
                print(f'refined query is: {refined_query}')
                context = find_match(refined_query)
                llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.1)
                conversation_text = context+"\n"+query
                response = llm.predict(conversation_text)
                
                #chat_history.append((query, response['response']))
                
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



@app.route('/api/test', methods=['GET'])
def test():
    if request.method == 'GET':
        # Get the 'message' query parameter from the URL
        message = request.args.get('message')

        # Check if 'message' parameter is provided
        if message:
            response_data = {
                "message": message,
                "status": "GET request received with 'message'",
            }
            return jsonify(response_data), 200
        else:
            response_data = {
                "error": "Missing 'message' parameter in the query",
            }
            return jsonify(response_data), 400


if __name__ == '__main__':
    app.run(debug=True)