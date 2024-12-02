from flask import Flask
from flask_cors import CORS
from .api.get_data_routes import get_data_routes

import os


app = Flask(__name__)

# OPTIMIZATION: scale for production
web_url=os.environ.get("WEB_URL")
CORS(app, origins=[web_url,"http://localhost:3000"])

app.register_blueprint(get_data_routes,url_prefix='/api/data')



if __name__ == '__main__':
    app.run(debug=True, port=5001)
    
