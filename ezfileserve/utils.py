from flask import current_app, flash
import os
import re

def delete_file(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File {filename} deleted.', 'success')
    else:
        flash(f'File {filename} not found.', 'error')

def list_uploaded_files():
    """Returns a sorted list of uploaded files, excluding .gitkeep."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return sorted(
        f for f in os.listdir(upload_folder)
        if f != '.gitkeep'
    )

def is_safe_filename(filename):
    #return '..' not in filename and '/' not in filename and '\\' not in filename
    return bool(re.match(r'^[\w.\- ]+$', filename))
