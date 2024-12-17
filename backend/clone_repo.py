from git import Repo
import os

def clone_repository(repo_url):
       repo_name = repo_url.split("/")[-1]
       repo_path = os.path.join(os.path.dirname(os.getcwd()), repo_name)

       # Check if the directory exists and is not empty
       if not os.path.exists(repo_path) and not os.listdir(repo_path):
           Repo.clone_from(repo_url, repo_path)
       return repo_path

path = clone_repository(os.environ.get("CLONE_REPO"))
print(f"Repository cloned to: {path}")
