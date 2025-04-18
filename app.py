from flask import Flask, render_template
from api_routes import api_routes
from flask_cors import CORS

app = Flask(__name__, template_folder="templates") 
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/api')
def api_docs():
    return render_template('index.html')

app.register_blueprint(api_routes)

if __name__ == "__main__":
    app.run(debug=True)
