from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from dotenv import load_dotenv
load_dotenv()

##using gemini flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

#using instructor embeddings from hugging face
instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
vectordb_file_path="faiss_index"

def create_vector_db():
    loader=CSVLoader(file_path='saakiai_faqs.csv',source_column='prompt')
    data=loader.load()
    ##using Faiss vector data base and passing data and embedding as input
    #first data from csv file is converted to embeddings and stored in db
    vectordb=FAISS.from_documents(documents=data,embedding=instructor_embeddings)
    vectordb.save_local(vectordb_file_path)

def get_qa_chain():
    vectordb=FAISS.load_local(vectordb_file_path,instructor_embeddings,allow_dangerous_deserialization=True)
    retriever=vectordb.as_retriever(score_threshold=0.7)

    prompt_template="""Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
    If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

    CONTEXT: {context}

    QUESTION: {question}

    """
    PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}

    
    chain = RetrievalQA.from_chain_type(llm=llm,
                                chain_type="stuff",
                                retriever=retriever,
                                input_key="query",
                                return_source_documents=True,
                                chain_type_kwargs=chain_type_kwargs)
    return chain


if __name__=="__main__":
    if not os.path.exists(f"{vectordb_file_path}.index"):
        create_vector_db()
    chain=get_qa_chain()
