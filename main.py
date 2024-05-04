from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os
from llama_index.llms.together import TogetherLLM
from llama_index.core.llms import ChatMessage
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import SimpleDirectoryReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
from qdrant.client import Client


# Text QA Prompt template construction
chat_text_qa_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
          
             "Always answer the query using the provided context information, "
            "and not prior knowledge.\n"
            

        ),
    ), 
    ChatMessage(
        role=MessageRole.USER,
        content=(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {query_str} in bullet points or numbered list where appropriate.\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)
    


def embed(): 
    #The below is for images and is not used in HR analytics. Leaving this here for reference. Only the text collection is stored and accessed for this project - Sasi
    

    llm = TogetherLLM(
                    model="togethercomputer/llama-2-70b-chat", api_key="96557b956acf6073510ee7e4abadc1c7863626e75278a0eaf9a747875af30604"
                )
            # %%
            # os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            # llm is set to togethercomputer/llama-2-70b-chat. Default is openAI. This can be changed to any other supported model.
    Settings.llm = llm
    

     #hugging face embedding mmodel is used using the llama index langchain integration (LangchainEmbedding)
    lc_embed_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
    )
    embed_model = LangchainEmbedding(lc_embed_model)
    Settings.embed_model = embed_model

    documents = SimpleDirectoryReader("./data").load_data()


    # Create a local Qdrant vector store
    # db = chromadb.PersistentClient(path="./chroma_db")

    # # Create collection
    # chroma_collection = db.get_or_create_collection("quickstart")

    # # Assign Chroma as the vector_store to the context
    # vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # storage_context = StorageContext.from_defaults(vector_store=vector_store)
    client = qdrant_client.QdrantClient(path="qdrant_db")
    vector_store = QdrantVectorStore(
        client=client, collection_name="text_collection")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create your index
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
   
   
    return index


# index is saved as a global variable to avoid re-creating it every time the query function is called
index = embed()
def handle_greetings(query):
    greetings = ["hi", "hello", "hey", "greetings", "morning", "afternoon", "evening"]
    return any(greeting == query.lower() for greeting in greetings)

def query(input):
    while True:
            query = input
            #top_k is set to 3 for the purpose of this project. This can be changed to a higher or lower value for better accuracy. This is the number of documents to be retrieved from the index.
           
           
            response = index.as_query_engine(text_qa_template=text_qa_template).query(query)
            print("user query: ", query)
            print("answer: ",response)
            return response
