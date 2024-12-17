import asyncio
from dotenv import load_dotenv
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.clone_repo import path

SUPPORTED_EXTENSIONS = {'.py', '.js', '.tsx', '.jsx', '.ipynb', '.java',
                        '.cpp', '.ts', '.go', '.rs', '.vue', '.swift', '.c', '.h'}

IGNORED_DIRS = {'node_modules', 'venv', 'env', 'dist', 'build', '.git',
                '__pycache__', '.next', '.vscode', 'vendor'}

load_dotenv()

def get_file_content(file_path, repo_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        relative_path = os.path.relpath(file_path, repo_path)
        return {
            "name": relative_path,
            "content": content
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None


def get_main_files_content(repo_path: str):
    files_content = []
    try:
        for root, _, files in os.walk(repo_path):
            # Skip if current directory is in ignored directories
            if any(ignored_dir in root for ignored_dir in IGNORED_DIRS):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file)[1] in SUPPORTED_EXTENSIONS:
                    file_content = get_file_content(file_path, repo_path)
                    if file_content:
                        files_content.append(file_content)
    except Exception as e:
        print(f"Error reading repository: {str(e)}")
    return files_content


async def embed_document():
    processed_data = []
    try:
        documents = []
        embedding_model = HuggingFaceEmbeddings()

        # Initialize Pinecone
        pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY")
        )
        
        index = pc.Index("codebase-rag")

        for file in get_main_files_content(path):
            doc = Document(
                page_content=f"{file['name']}\n{file['content']}",
                metadata={"source": file['name']}
            )

            documents.append(doc)
            
            embedding = embedding_model.embed_documents([doc.page_content])[0]

            processed_data.append({
                "id": file["name"],  
                "values": embedding,
                "metadata": {"source": file["name"], "content": doc.page_content}
            })

        # Upsert data to Pinecone
        if processed_data:
            index.upsert(vectors=processed_data, namespace=os.environ.get("PINECONE_NAMESPACE"))

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(embed_document())
