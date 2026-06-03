import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from app.models import mongo
from app.routes.scan import scan_bp 
from app.routes.dashboard import dashboard_bp

# Load environment variables dari file .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app) # Mengizinkan frontend (Edge/Chrome) menembak API ini

    # Konfigurasi dari Environment Variables
    # Menggunakan nilai default jika variabel tidak ditemukan di .env
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/zonaPanganDB")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key-for-dev")
    
    # Inisialisasi Database
    mongo.init_app(app)
    
    # Debug koneksi database
    with app.app_context():
        try:
            mongo.db.command('ping')
            print("--- Berhasil terhubung ke MongoDB: " + app.config["MONGO_URI"].split('/')[-1] + " ---")
        except Exception as e:
            print(f"--- Gagal terhubung ke MongoDB: {e} ---")

    # Blueprint Registrations
    app.register_blueprint(scan_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Endpoint tidak ditemukan"}), 404

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "Terjadi kesalahan internal pada server"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Menggunakan host='0.0.0.0' agar bisa diakses oleh HP fisik di jaringan Wi-Fi yang sama
    app.run(debug=True, host='0.0.0.0', port=5000)