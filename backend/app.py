from flask import Flask
from flask_cors import CORS
from .api.get_data_routes import get_data_routes
from .api.clone_repo_routes import clone_repo_routes
import os


app = Flask(__name__)


CORS(app, origins=["http://localhost:3000"])

app.register_blueprint(get_data_routes,url_prefix='/api/data')
app.register_blueprint(clone_repo_routes,url_prefix='/api/data')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
