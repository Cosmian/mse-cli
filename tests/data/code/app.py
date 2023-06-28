from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    """Get a simple example."""
    return "Hello world"
