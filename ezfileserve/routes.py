import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, abort
from urllib.parse import quote, unquote
from .utils import delete_file, list_uploaded_files, is_safe_filename

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    uploaded = request.args.get('uploaded')
    error = request.args.get('error')
    files = list_uploaded_files()
    raw_hosts = current_app.config.get('HOSTS')
    host_list = [h.strip() for h in raw_hosts.split(',') if h.strip()]
    file_links = {
        f: [
            { "url": f"{host}{url_for('routes.uploaded_file', filename=f)}",
            "host": host } 
            for host in host_list
            ]
        for f in files
    }
    return render_template('index.html', file_links=file_links,
                           auth_required=current_app.config.get('UPLOAD_AUTH_REQUIRED', True))

@bp.route('/upload', methods=['POST'])
def upload():
    if current_app.config.get('UPLOAD_AUTH_REQUIRED', True):
        password = request.form.get('upload_password', '')
        if password != current_app.config['UPLOAD_PASSWORD']:
            flash('Unauthorized: incorrect password!', 'error')
            return redirect(url_for('routes.admin'))

    files = request.files.getlist('file')
    uploaded_count = 0

    for file in files:
        if not file or file.filename == '':
            continue
        if not is_safe_filename(file.filename):
            flash(f"Invalid filename: {file.filename}", "error")
            continue
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
        uploaded_count += 1
    if uploaded_count == 0:
        flash('No file uploaded', 'warning')
    elif uploaded_count == 1:
        flash('1 file uploaded', 'success')
    elif uploaded_count > 1:
        flash(f'{uploaded_count} files uploaded', 'success')

    return redirect(url_for('routes.admin'))

@bp.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if not current_app.config.get('ENABLE_ADMIN', False):
        abort(404)

    auth_required = current_app.config.get('ADMIN_AUTH_REQUIRED', True)
    upload_auth_required = current_app.config.get('UPLOAD_AUTH_REQUIRED', True)

    if request.method == 'POST':
        if auth_required:
            password = request.form.get('delete_password', '')
            if password != current_app.config['ADMIN_PASSWORD']:
                flash('Unauthorized: incorrect password!', 'error')
                files = list_uploaded_files()
                return redirect(url_for('routes.admin'))

        if 'delete_single' in request.form:
            delete_file(request.form.get('delete_single'))
        elif 'delete_selected' in request.form:
            selected_files = request.form.getlist('selected_files')
            if not selected_files:
                flash('No files selected.', 'error')
            else:
                for f in selected_files:
                    delete_file(f)

        # ✅ Redirect after successful POST to avoid resubmission
        return redirect(url_for('routes.admin'))

    # GET request
    files = list_uploaded_files()
    return render_template('admin.html', files=files, 
                        upload_auth_required=upload_auth_required, 
                        admin_auth_required=auth_required)


# @bp.route('/test-toasts')
# def test_toasts():
#     flash("Success message", "success")
#     flash("Error message", "error")
#     flash("Info message", "info")
#     flash("Warning message", "warning")
#     return redirect(url_for('routes.index'))
