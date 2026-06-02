from flask import Blueprint, request, jsonify
from app.models import mongo
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    company_name = data.get('company_name')

    print(f"DEBUG: Menerima request registrasi untuk: {email}") # LOGGING

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email sudah terdaftar"}), 400
    
    if role == 'manager':
        if not mongo.db.companies.find_one({"name": company_name}):
            mongo.db.companies.insert_one({"name": company_name})
            print(f"DEBUG: Perusahaan {company_name} berhasil ditambahkan ke koleksi companies")
            
    elif role == 'operator':
        if not mongo.db.companies.find_one({"name": company_name}):
            return jsonify({"error": "Perusahaan tidak ditemukan"}), 400
    else:
        return jsonify({"error": "Role tidak valid"}), 400

    new_user = {
        "username": username,
        "email": email,
        "password": generate_password_hash(password),
        "role": role,
        "company_name": company_name
    }
    
    # EKSEKUSI INSERT
    try:
        result = mongo.db.users.insert_one(new_user)
        print(f"DEBUG: User berhasil disimpan dengan ID: {result.inserted_id}")
        return jsonify({"message": "Registrasi berhasil"}), 201
    except Exception as e:
        print(f"DEBUG ERROR: Gagal menyimpan ke MongoDB: {e}")
        return jsonify({"error": "Gagal menyimpan data ke database"}), 500

# Rute tambahan untuk Frontend mengambil daftar perusahaan
@auth_bp.route('/companies', methods=['GET'])
def get_companies():
    # Mengambil hanya nama perusahaan dari koleksi 'companies'
    companies = list(mongo.db.companies.find({}, {"_id": 0, "name": 1}))
    return jsonify(companies), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Gunakan 'identifier' atau 'email_or_username' dari frontend
    identifier = data.get('email')  # Tetap pakai 'email' key-nya agar kompatibel
    password = data.get('password')
    
    # Mencari user berdasarkan email ATAU username
    user = mongo.db.users.find_one({
        "$or": [
            {"email": identifier},
            {"username": identifier}
        ]
    })
    
    if user and check_password_hash(user['password'], password):
        return jsonify({
            "message": "Login berhasil",
            "username": user.get('username'),
            "role": user['role'],
            "company_name": user['company_name']
        }), 200
        
    print(f"DEBUG: Login gagal untuk identifier: {identifier}")
    return jsonify({"error": "Email/Username atau password salah"}), 401
    
# Forgot Password: Generate token dan simpan di database
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    user = mongo.db.users.find_one({"email": email})
    
    if not user:
        return jsonify({"error": "Email tidak ditemukan"}), 404
    
    token = str(uuid.uuid4())
    mongo.db.users.update_one({"email": email}, {"$set": {"reset_token": token}})
    
    # Tambahkan ini agar Anda tahu token apa yang baru saja dibuat
    print(f"DEBUG: Token baru telah dibuat untuk {email}: {token}")
    
    return jsonify({"message": "Token reset password berhasil dibuat", "token": token}), 200

# Reset Password: Gunakan token untuk ganti password
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')
    
    print(f"DEBUG: Mencoba mereset password dengan token: {token}")
    
    user = mongo.db.users.find_one({"reset_token": token})
    if not user:
        print(f"DEBUG: Token {token} tidak ditemukan di database.")
        return jsonify({"error": "Token tidak valid atau kadaluarsa"}), 400
    
    hashed_password = generate_password_hash(new_password)
    mongo.db.users.update_one(
        {"reset_token": token}, 
        {"$set": {"password": hashed_password}, "$unset": {"reset_token": ""}}
    )
    
    print(f"DEBUG: Password untuk user {user.get('email')} berhasil direset.")
    return jsonify({"message": "Password berhasil direset"}), 200