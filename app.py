from flask import Flask, render_template, request, jsonify, session,redirect, url_for
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader, get_response_synthesizer
from llama_index.core import DocumentSummaryIndex
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
# from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage,MessageRole
from llama_index.llms.together import TogetherLLM
import os
from llama_index.core.indices.document_summary import (
    DocumentSummaryIndexLLMRetriever,
)
import re
from llama_index.core.query_engine import RetrieverQueryEngine
import PyPDF2
import shutil
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

import os
from main import query
app = Flask(__name__, static_folder='static',template_folder='templates')
app.secret_key = b'+A\xb8\x85\xddL#\xa4{\xc7\x15\xbcH\xa8Im\xe1\x17E\xc4\xd3\x06\xc6\xd8'



def main(input):
    if 'chat_history' not in session:
        session['chat_history'] = []

    chat_history = session['chat_history']

    if input == "exit":
        answer = "Goodbye!"
    
    else:
        response = query(input)
        answer = str(response)

        if answer is not None:
            formatted_answer = format_answer(answer)
            chat_history.append({"question": input, "answer": formatted_answer})
            session['chat_history'] = chat_history  # Update the chat history in the session
        else:
            answer = "No answer found"

    return answer, chat_history







def format_answer(answer):
    lines = answer.split('\n')
    formatted_lines = []
    in_list = False
    list_type = None

    for line in lines:
        # Check for numbered list
        numbered_match = re.match(r'^(\d+\.\s)(.+)', line)
        # Check for asterisk list
        asterisk_match = re.match(r'^(\*\s)(.+)', line)
        # Split asterisk list items that are on the same line
        asterisk_items = re.findall(r'\*\s(.+?)(?=(\*\s|$))', line)

        if numbered_match:
            if not in_list or list_type != 'ol':
                if in_list:  # Close the previous list
                    formatted_lines.append('</ul>' if list_type == 'ul' else '</ol>')
                formatted_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            formatted_lines.append(f'<li>{numbered_match.group(2).strip()}</li>')

        elif asterisk_match or asterisk_items:
            if not in_list or list_type != 'ul':
                if in_list:  # Close the previous list
                    formatted_lines.append('</ol>' if list_type == 'ol' else '</ul>')
                formatted_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            if asterisk_items:
                for item, _ in asterisk_items:
                    formatted_lines.append(f'<li>{item.strip()}</li>')
            else:
                formatted_lines.append(f'<li>{asterisk_match.group(2).strip()}</li>')

        else:
            if in_list:  # Close the previous list
                formatted_lines.append('</ul>' if list_type == 'ul' else '</ol>')
                in_list = False
            # Wrap non-list lines in paragraphs or handle them appropriately
            formatted_lines.append(f'<p>{line.strip()}</p>')

    # Close any open list tags
    if in_list:
        formatted_lines.append('</ul>' if list_type == 'ul' else '</ol>')

    # Combine all formatted lines
    formatted_output = ''.join(formatted_lines)

    return formatted_output

# @app.route('/submit', methods=['POST'])
# def handle_submit():
#     input = request.form.get('user_input')
#     answer, chat_history = main(input)
#     print("chat:", chat_history)
#     session['chat_history'] = chat_history
#     return render_template('athenachat.html', query=input, answer=answer, query_history=chat_history)

@app.route('/submit', methods=['POST'])

def handle_submit():
    try:
        input = request.form.get('user_input')
        answer, chat_history = main(input)
        print("chat:", chat_history)
        session['chat_history'] = chat_history
        return render_template('athenachat.html', query=input, answer=answer, query_history=chat_history)
    except Exception as e:
        print("An error occurred:", e)
        return "An error occurred: " + str(e)








@app.route('/')
def index():
    return render_template('index.html',)
@app.route('/doc')
def doc():
    return render_template('doc.html')
@app.route('/doc_chat')
def doc_chat():
    return render_template('doc_chat.html')
@app.route('/athena_chat')
def athena_chat():
    return render_template('athenachat.html')

if __name__ == '__main__':
    app.run(port = 7000, debug=False)
