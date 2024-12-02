from flask import Flask, request, jsonify, Blueprint
import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from git import Repo
import json

load_dotenv()

get_data_routes = Blueprint('get_data', __name__)

# Set the PINECONE_API_KEY as an environment variable
pinecone_api_key = os.getenv("PINECONE_API_KEY")
os.environ['PINECONE_API_KEY'] = pinecone_api_key

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
pinecone_index = pc.Index("codebase-rag")

SUPPORTED_EXTENSIONS = {'.py', '.js', '.tsx', '.jsx', '.ipynb', '.java',
                         '.cpp', '.ts', '.go', '.rs', '.vue', '.swift', '.c', '.h'}

IGNORED_DIRS = {'node_modules', 'venv', 'env', 'dist', 'build', '.git',
                '__pycache__', '.next', '.vscode', 'vendor'}


def clone_repository(repo_url):
    
    repo_name = repo_url.split("/")[-1] 
    repo_path = f"/content/{repo_name}"
    Repo.clone_from(repo_url, str(repo_path))
    return str(repo_path)

path = clone_repository("https://github.com/CoderAgent/SecureAgent")

def get_file_content(file_path, repo_path):
 
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get relative path from repo root
        rel_path = os.path.relpath(file_path, repo_path)

        return {
            "name": rel_path,
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

def perform_rag(query):
    raw_query_embedding = get_huggingface_embeddings(query)
    top_matches = pinecone_index.query(vector=raw_query_embedding.tolist(), top_k=5, include_metadata=True)
    contexts = [item['metadata']['text'] for item in top_matches['matches']]
    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + query
    system_prompt = f"""You are a Senior Software Engineer, specializing in TypeScript.
    Answer any questions I have about the codebase, based on the code provided. Always consider all of the context provided when forming a response."""
    
    client = OpenAI(api_key=os.getenv("GROQ_API_KEY"))
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
    query = data.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    response = perform_rag(query)
    return jsonify({"response": response}), 200

# Initialize the Flask app
app = Flask(__name__)
app.register_blueprint(get_data_routes)

if __name__ == '__main__':
    app.run(debug=True)