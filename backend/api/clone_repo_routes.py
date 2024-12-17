from git import Repo
import os
from flask import Blueprint, request
from backend.pinecone_embed_document import embed_document

clone_repo_routes = Blueprint('clone_repo', __name__)

@clone_repo_routes.route('/clone-repo', methods=['POST'])
def clone_repository():
        repo_url = request.json.get('codebaseURL')
        print("repo_url",repo_url)
        repo_name = repo_url.split("/")[-1]
        repo_path = os.path.join(os.path.dirname(os.getcwd()), repo_name)

     
        if not os.path.exists(repo_path):
            Repo.clone_from(repo_url, repo_path)
            # call pinecone_embed_document
        embed_document(repo_path,repo_url)
        return repo_path

# path = clone_repository()

# os.environ.get("CODEBASE_URL")
# print(f"Repository cloned to: {path}")
