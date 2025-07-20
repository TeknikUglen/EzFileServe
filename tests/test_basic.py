import os
import io
import tempfile
import pytest

from ezfileserve import create_app

@pytest.fixture
def client():
    with tempfile.TemporaryDirectory() as tmp_uploads:
        app = create_app(upload_folder_override=tmp_uploads)
        app.config['UPLOAD_PASSWORD'] = 'yourpassword'
        app.config['ADMIN_PASSWORD'] = 'yourpassword'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
        app.config['WTF_CSRF_ENABLED'] = False  # in case you add forms later
        app.config['ENABLE_ADMIN'] = True

        with app.test_client() as client:
            yield client


def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Available Files' in rv.data

def test_upload_with_correct_password(client):
    data = {
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy content"), 'test.txt'),
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200
    assert b'test.txt' in rv.data

def test_upload_with_wrong_password(client):
    data = {
        'upload_password': 'wrongpassword',
        'file': (io.BytesIO(b"dummy content"), 'fail.txt'),
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200
    assert b'Unauthorized: incorrect password' in rv.data

def test_upload_with_invalid_filename(client):
    data = {
        'upload_password': 'yourpassword',
        'file': [(io.BytesIO(b"dummy content"), 'test%//test2.txt')],
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid filename: test%//test2.txt' in rv.data

def test_uploaded_file_appears_on_index(client):
    # Upload a file first
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    # Check that the uploaded file link appears on the index page
    rv = client.get('/')
    assert b'visible.txt' in rv.data

def test_admin_page_loads(client):
    rv = client.get('/admin')
    assert rv.status_code == 200
    assert b'Admin Area' in rv.data

def test_uploaded_file_appears_on_admin(client):
    # Upload a file first
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    # Check that the uploaded file link appears on the index page
    rv = client.get('/admin')
    assert b'visible.txt' in rv.data

def test_delete_file_is_gone_on_admin(client):
    # Upload a file first
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    # Check that the uploaded file link appears on the index page
    rv = client.get('/admin')
    assert b'visible.txt' in rv.data

    client.post('/admin', data={
        'delete_password': 'yourpassword',
        'selected_files': ['visible.txt'],
        'delete_selected': '1',
    }, content_type='multipart/form-data', follow_redirects=True)

    # Check that the uploaded file link no longer appears on the admin page
    rv = client.get('/admin')
    assert b'visible.txt' not in rv.data

    # Check that the uploaded file link no longer appears on the index page
    rv = client.get('/')
    assert b'visible.txt' not in rv.data


def test_delete_with_wrong_password_fails(client):
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    rv = client.post('/admin', data={
        'delete_password': 'wrongpassword',
        'selected_files': ['visible.txt'],
        'delete_selected': '1',
    }, content_type='multipart/form-data', follow_redirects=True)

    assert b'visible.txt' in rv.data  # File still present

def test_single_file_delete_button(client):
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    client.post('/admin', data={
        'delete_password': 'yourpassword',
        'delete_single': 'visible.txt',
    }, content_type='multipart/form-data', follow_redirects=True)

    rv = client.get('/admin')
    assert b'visible.txt' not in rv.data

def test_delete_selected_without_selecting_file_does_nothing(client):
    # Upload a file to make sure something exists
    client.post('/upload', data={
        'upload_password': 'yourpassword',
        'file': (io.BytesIO(b"dummy"), 'visible.txt'),
    }, content_type='multipart/form-data', follow_redirects=True)

    # Post with delete_selected but no selected_files
    client.post('/admin', data={
        'delete_password': 'yourpassword',
        'delete_selected': '1',
        # No 'selected_files' sent
    }, content_type='multipart/form-data', follow_redirects=True)

    # File should still be listed
    rv = client.get('/admin')
    assert b'visible.txt' in rv.data

