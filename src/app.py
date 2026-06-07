from flask import Flask
from src.routes import riders_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(riders_bp)
    return app