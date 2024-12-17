from flask import request, jsonify, Blueprint
import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

get_data_routes = Blueprint('get_data', __name__)
client = OpenAI(base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv("GROQ_API_KEY"))
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))


def get_huggingface_embeddings(text, model_name="sentence-transformers/all-mpnet-base-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

def perform_rag(user_prompt):
    raw_query_embedding = get_huggingface_embeddings(user_prompt)
    print("raw_query_embedding.tolist()",raw_query_embedding.tolist())
    index = pc.Index(os.environ.get("PINECONE_INDEX"))
    top_matches = index.query(vector=raw_query_embedding.tolist(), top_k=5, include_metadata=True, namespace="https://github.com/CoderAgent/SecureAgent")
   
    contexts = [item['metadata']['content'] for item in top_matches['matches']]
    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + user_prompt
    system_prompt = os.environ.get("SYSTEM_PROMPT")
    
    
    llm_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_query}
        ]
    )
    return llm_response.choices[0].message.content


@get_data_routes.route('/ai-response', methods=['POST'])
def perform_rag_route():
    data = request.json
    if not data:
            return jsonify({"error": "No data provided"}), 400
        
    user_prompt=data.get('userPrompt',"")
    print("user_prompt",user_prompt)
    if not user_prompt:
        return jsonify({"error": "User prompt is required"}), 400


    response = perform_rag(user_prompt)
    return response


