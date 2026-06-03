from flask import Blueprint, request, jsonify, send_file
from app.ai_engine.scanner import FruitScanner 
from app.models import get_scan_logs_col
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
    username = request.form.get('username', 'Unknown User')
    item_count = int(request.form.get('item_count', 0))
    operator_email = request.form.get('operator_email', 'unknown@email.com')

    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.jpg")
    file.save(file_path)

    try:
        import base64
        scan_output = scanner.scan(file_path) 
        detections = scan_output.get("detections", [])
        
        if detections and isinstance(detections, list):
            draw_boxes(file_path, detections)
            has_bad = any('bad' in res.get('label', '').lower() or 'anomali' in res.get('label', '').lower() for res in detections)
            
            log_data = {
                "username": username,
                "operator_email": operator_email,
                "item_count": item_count,
                "prediction": detections[0].get('label') if detections else "Unknown",
                "is_safe": not has_bad, 
                "timestamp": datetime.utcnow(),
                "status": "pending_review"
            }
            get_scan_logs_col().insert_one(log_data)
            
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            return jsonify({
                "message": "Scan berhasil",
                "prediction": log_data["prediction"],
                "is_safe": log_data["is_safe"],
                "detections": detections,
                "image_base64": encoded_string
            }), 200
        
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