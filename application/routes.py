import json
import uuid
from datetime import datetime, timedelta
from functools import wraps

import jwt
from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess
from azure.storage.queue import QueueServiceClient, TextBase64EncodePolicy
from flask import request, jsonify
from flask_cors import cross_origin
from sqlalchemy import or_
from transliterate import translit

from application import app, db
from application.models import User

STORAGE_CONNECTION_STRING = app.config['STORAGE_CONNECTION_STRING']


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query.filter_by(login=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(
                expired_msg), 401  # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return jsonify({'status': 'initialized'})


@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    data = request.get_json()
    if User.query.filter(or_(User.email == data['email'],
                             User.login == data['login'])).first():
        return jsonify(
            {'message': 'User with the same email or login is existed.'}), 209

    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user.jsonify(), 201


@app.route('/signin', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify(
            {'message': 'Invalid credentials: wrond login or password',
             'authenticated': False}), 401

    token = jwt.encode({
        'sub': user.login,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=30)},
        app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})


@app.route('/photocards', methods=['GET'])
@cross_origin()
@token_required
def get_files(current_user):
    blob_service_client = BlobServiceClient.from_connection_string(
        STORAGE_CONNECTION_STRING)

    container_name = current_user.login
    container_client = blob_service_client.get_container_client(container_name)
    if not any(container.name == container_name for container in
               blob_service_client.list_containers()):
        container_client.create_container(public_access=PublicAccess.Blob)

    photoCards = []
    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob.name)
        photoCards.append(
            {'name': blob_client.blob_name, 'url': blob_client.url})
    return jsonify({'photoCards': photoCards})


@app.route('/photocards', methods=['POST'])
@cross_origin()
@token_required
def upload_files(current_user):
    blob_service_client = BlobServiceClient.from_connection_string(
        STORAGE_CONNECTION_STRING)

    container_name = current_user.login
    container_client = blob_service_client.get_container_client(container_name)
    if not any(container.name == container_name for container in
               blob_service_client.list_containers()):
        container_client.create_container(public_access=PublicAccess.Blob)

    files = request.files

    for file in files.values():
        # Transliteration of filename
        filename = translit(file.filename, 'ru', reversed=True)

        blob_name = str(uuid.uuid4())
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file, content_settings=ContentSettings(
            content_type=file.content_type,
            content_disposition='attachment;filename=' + filename))
    return jsonify({'number_files': len(files)})


@app.route('/photocards', methods=['DELETE'])
@cross_origin()
@token_required
def delete_file(current_user):
    blob_service_client = BlobServiceClient.from_connection_string(
        STORAGE_CONNECTION_STRING)

    container_name = current_user.login
    container_client = blob_service_client.get_container_client(container_name)
    if not any(container.name == container_name for container in
               blob_service_client.list_containers()):
        container_client.create_container(public_access=PublicAccess.Blob)

    blob_client = container_client.get_blob_client(request.args.get('name'))
    blob_client.delete_blob()
    return jsonify({'number_files': 1, 'name': blob_client.blob_name})


@app.route('/crop', methods=['POST'])
@cross_origin()
@token_required
def crop_photo(current_user):
    queue_service_client = QueueServiceClient.from_connection_string(
        STORAGE_CONNECTION_STRING)

    queue_name = 'crop-queue'
    queue_client = queue_service_client.get_queue_client(queue_name)
    if not any(queue.name == queue_name for queue in
               queue_service_client.list_queues()):
        queue_client.create_queue()

    data = request.get_json()

    message = {
        'container_name': current_user.login,
        'blob_name': data.get('name'),
        'queue_name': current_user.login,
        'crop_config': data.get('crop_config')
    }
    base64_encoder = TextBase64EncodePolicy()
    queue_client.send_message(base64_encoder.encode(json.dumps(message)),
                              visibility_timeout=0)
    return jsonify({'uuid': data.get('name')})
