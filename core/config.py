import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pokja_pemilihan_secret_key_2026_xyz')
    
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "data", "pokja.db")}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'output_dokumen')
    TEMPLATE_DOC_FOLDER = os.path.join(BASE_DIR, 'templates_dokumen')