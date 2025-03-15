from flask import Flask
from api_routes import api_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(api_routes)

if __name__ == "__main__":
    app.run()
