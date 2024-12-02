import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv


load_dotenv()

def main():

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable is not set.")


    pc = Pinecone(api_key=pinecone_api_key)


    pinecone_index = pc.Index("codebase-rag")


    vectorstore = PineconeVectorStore(index_name="codebase-rag", embedding=HuggingFaceEmbeddings())

    file_content = [
        {"name": "example_file.py", "content": "print('Hello, World!')"},
    
    ]

    documents = []

    for file in file_content:
        doc = Document(
            page_content=f"{file['name']}\n{file['content']}",
            metadata={"source": file['name']}
        )
        documents.append(doc)

   
    vectorstore = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=HuggingFaceEmbeddings(),
        index_name="codebase-rag",
        namespace="https://github.com/CoderAgent/SecureAgent"
    )

    print("Documents embedded and uploaded to Pinecone successfully.")

if __name__ == "__main__":
    main()