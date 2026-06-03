from flask import Blueprint, request, jsonify
from app.models import get_scan_logs_col
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# --- 1. Dashboard Utama (Overview) ---
@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    company = request.args.get('company_name')
    if not company: return jsonify({"error": "Nama perusahaan diperlukan"}), 400
    company = company.strip() # Sinkronisasi dengan .trim() di ApiService

    pipeline = [
        {"$match": {"company_name": company}},
        {"$group": {"_id": "$prediction", "count": {"$sum": 1}, "total_items": {"$sum": {"$toInt": "$item_count"}}}}
    ]
    stats = list(get_scan_logs_col().aggregate(pipeline))
    
    # Menghitung food waste dengan penanganan data null/kosong yang aman
    food_waste = sum(int(item.get('total_items', 0)) for item in stats if "bad" in str(item.get('_id', '')).lower())
    
    return jsonify({"stats": stats, "food_waste_items": int(food_waste)})

# --- 2. Manajemen Inventaris (FIFO & Alert) ---
@dashboard_bp.route('/inventory', methods=['GET'])
def get_inventory():
    company = request.args.get('company_name')
    if company: company = company.strip() # Sinkronisasi dengan .trim() di ApiService
    status = request.args.get('status')
    
    query = {"company_name": company}
    if status: query["status"] = status
        
    cursor = get_scan_logs_col().find(query).sort("timestamp", 1)
    
    data = []
    for item in cursor:
        prediction = str(item.get('prediction', '')).lower()
        alert = "bad" in prediction
        
        data.append({
            "id": str(item['_id']),
            "prediction": item.get('prediction', 'Unknown'),
            "item_count": item.get('item_count', 0),
            "status": item.get('status', 'pending_review'),
            "date": item['timestamp'].strftime("%Y-%m-%d") if isinstance(item.get('timestamp'), datetime) else "N/A",
            "alert": alert
        })
    return jsonify({"inventory": data})

# --- 3. Riwayat Log (Audit Trail) ---
@dashboard_bp.route('/logs', methods=['GET'])
def get_audit_logs():
    company = request.args.get('company_name')
    if company: company = company.strip() # Sinkronisasi dengan .trim() di ApiService
    status = request.args.get('status')
    
    query = {"company_name": company}
    if status: query["status"] = status
        
    logs = list(get_scan_logs_col().find(query).sort("timestamp", -1))
    
    for log in logs:
        log['_id'] = str(log['_id'])
        log['username'] = log.get('username', 'Unknown')
        log['status'] = log.get('status', 'pending_review')
        log['timestamp'] = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(log.get('timestamp'), datetime) else "N/A"
        
    return jsonify({"logs": logs})