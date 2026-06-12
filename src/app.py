from flask import Flask, render_template
from src.routes import riders_bp
from src.postgres.postgres_handlers import inizializza_db, esegui_reset_db
import sys
import os

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )
    try:
        inizializza_db()
        esegui_reset_db()
    except Exception as e:
        print(f"ERRORE DI AVVIO: Impossibile connettersi a PostgreSQL. \nDettaglio: {e}")
        sys.exit(1)
    app.register_blueprint(riders_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app