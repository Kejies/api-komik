from flask import Flask
from api_routes import api_routes  # Pastikan ada ini

app = Flask(__name__)
app.register_blueprint(api_routes)

if __name__ == "__main__":
    app.run()
