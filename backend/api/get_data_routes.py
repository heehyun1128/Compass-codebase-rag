from flask import Flask, request, jsonify, Blueprint
import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from git import Repo
import json
from backend.clone_repo import path

load_dotenv()

get_data_routes = Blueprint('get_data', __name__)
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"))
# Set the PINECONE_API_KEY as an environment variable
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
pinecone_index = pc.Index("codebase-rag")

SUPPORTED_EXTENSIONS = {'.py', '.js', '.tsx', '.jsx', '.ipynb', '.java',
                         '.cpp', '.ts', '.go', '.rs', '.vue', '.swift', '.c', '.h'}

IGNORED_DIRS = {'node_modules', 'venv', 'env', 'dist', 'build', '.git',
                '__pycache__', '.next', '.vscode', 'vendor'}


def get_file_content(file_path, repo_path):
    try:
        with open(file_path,"r",encoding="utf-8") as file:
            content=file.read()
            
        relative_path=os.path.relpath(file_path,repo_path)
        
        return {
            "name":relative_path,
            "content":content
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

            # Process each file in current directory
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file)[1] in SUPPORTED_EXTENSIONS:
                    file_content = get_file_content(file_path, repo_path)
                    if file_content:
                        files_content.append(file_content)

    except Exception as e:
        print(f"Error reading repository: {str(e)}")

    return files_content

file_content = get_main_files_content(path)

def get_huggingface_embeddings(text, model_name="sentence-transformers/all-mpnet-base-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

def perform_rag(user_prompt):
    res=client.embeddings.create(
            model="text-embedding-3-small",
            input=[user_prompt]
        )
    raw_query_embedding = res.data[0].embedding
    top_matches = pinecone_index.query(vector=raw_query_embedding.tolist(), top_k=5, include_metadata=True)
    contexts = [item['metadata']['text'] for item in top_matches['matches']]
    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + query
    system_prompt = f"""You are a Senior Software Engineer, specializing in TypeScript.
    Answer any questions I have about the codebase, based on the code provided. Always consider all of the context provided when forming a response."""
    
    
    llm_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_query}
        ]
    )
    return llm_response.choices[0].message.content

# Define a single route to perform RAG
@get_data_routes.route('/ai-response', methods=['POST'])
def perform_rag_route():
    data = request.json
    if not data:
            return jsonify({"error": "No data provided"}), 400
        
    user_prompt=data.get('userPrompt',"")
    
    if not user_prompt:
        return jsonify({"error": "User prompt is required"}), 400


    response = perform_rag(user_prompt)
    return jsonify({"response": response}), 200


