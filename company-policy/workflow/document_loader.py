from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_RETRIEVER_K = 4

def load_chunk_and_create_retriever(chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP, retriever_k=DEFAULT_RETRIEVER_K):
    pdf_files = [
        "company-files/code-of-conduct.pdf",
        "company-files/company-events.pdf",
        "company-files/company-policies.pdf"
    ]

    all_chunks = []
    for pdf_file in pdf_files:
        print(f"Loading PDF: {pdf_file}")
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)
        print(f"Chunked {pdf_file} into {len(chunks)} pieces")

        all_chunks.extend(chunks)
    
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": retriever_k})
    print(f"Retriever created with top {retriever_k} chunks per query")
    return retriever