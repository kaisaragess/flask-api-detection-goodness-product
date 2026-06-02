from flask_pymongo import PyMongo

# Inisialisasi object mongo
mongo = PyMongo()

# Helper untuk mengakses database
def get_db():
    return mongo.db

# Fungsi helper untuk koleksi 'users'
def get_users_col():
    return mongo.db.users

# Fungsi helper untuk koleksi 'scan_logs'
def get_scan_logs_col():
    return mongo.db.scan_logs

def get_companies_col():
    return mongo.db.companies