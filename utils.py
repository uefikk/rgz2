import os
from werkzeug.utils import secure_filename
from datetime import datetime

def save_uploaded_file(uploaded_file, upload_folder):
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]  # уникальная временная метка
        unique_filename = f"{timestamp}_{os.path.splitext(filename)[0]}.{filename.rsplit('.', 1)[-1]}"
        file_path = os.path.join(upload_folder, unique_filename)
        uploaded_file.save(file_path)
        return unique_filename
    return None