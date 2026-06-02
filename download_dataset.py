import os
from dotenv import load_dotenv
from roboflow import Roboflow

# 1. Load variabel dari .env
load_dotenv()

# 2. Ambil API Key dengan aman
api_key = os.getenv("ROBOFLOW_API_KEY")

if not api_key:
    raise ValueError("API Key tidak ditemukan! Pastikan file .env sudah diisi.")

# 3. Gunakan variabel tersebut
rf = Roboflow(api_key=api_key)
project = rf.workspace("kelompoks-workspace-p18ds").project("rotten-fruit-detector-2ds7u")
version = project.version(1)
dataset = version.download("yolov8")