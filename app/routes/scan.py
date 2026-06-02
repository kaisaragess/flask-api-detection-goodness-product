from flask import Blueprint, request, jsonify, send_file
from app.ai_engine.scanner import FruitScanner 
from app.models import get_scan_logs_col, get_users_col # Import get_users_col
import os
import uuid
import cv2
from datetime import datetime

scan_bp = Blueprint('scan', __name__)
scanner = FruitScanner() 
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def draw_boxes(image_path, results):
    img = cv2.imread(image_path)
    for res in results:
        label = res.get('label', 'unknown').lower()
        box = res.get('box', []) 
        if not box or len(box) < 4: continue
        
        is_good = 'good' in label
        color = (0, 255, 0) if is_good else (0, 0, 255)
        
        cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, 3)
        cv2.putText(img, label, (int(box[0]), int(box[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    cv2.imwrite(image_path, img)

@scan_bp.route('/scan', methods=['POST'])
def scan_fruit():
    if 'file' not in request.files: return jsonify({"error": "Tidak ada file"}), 400
    
    file = request.files['file']
    username = request.form.get('username')
    company_name = request.form.get('company_name')
    weight = float(request.form.get('weight', 0))

    # --- LOGIKA AMBIL EMAIL OTOMATIS DARI DB USERS ---
    user_record = get_users_col().find_one({"username": username})
    operator_email = user_record.get('email', 'unknown@email.com') if user_record else "unknown@email.com"
    # --------------------------------------------------

    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.jpg")
    file.save(file_path)

    try:
        results = scanner.scan(file_path) 
        if results and isinstance(results, list):
            draw_boxes(file_path, results)
            has_bad = any('bad' in res.get('label', '').lower() for res in results)
            
            log_data = {
                "company_name": company_name, 
                "username": username,
                "operator_email": operator_email, # Email sekarang otomatis terisi
                "weight": weight,
                "prediction": results[0].get('label') if results else "Unknown",
                "is_safe": not has_bad, 
                "timestamp": datetime.utcnow(),
                "status": "pending_review" 
            }
            get_scan_logs_col().insert_one(log_data)
            
            return send_file(file_path, mimetype='image/jpeg')
        
        return jsonify({"error": "Tidak ada objek terdeteksi"}), 422
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@scan_bp.route('/confirm-scan', methods=['POST'])
def confirm_scan():
    try:
        data = request.get_json()
        username = data.get('username')
        
        # Mencari log terbaru berdasarkan username
        last_log = get_scan_logs_col().find(
            {"username": username}
        ).sort("timestamp", -1).limit(1)
        
        logs_list = list(last_log)
        if not logs_list:
            return jsonify({"error": "Log tidak ditemukan"}), 404
            
        get_scan_logs_col().update_one(
            {"_id": logs_list[0]['_id']}, 
            {"$set": {"status": "verified"}}
        )
        
        return jsonify({"message": "Berhasil diverifikasi"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500