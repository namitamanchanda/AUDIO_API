from flask import Flask, request, make_response
from pymongo import MongoClient
import json
from gridfs import GridFS
from bson.objectid import ObjectId

app = Flask(__name__)

mongodb_client = MongoClient("mongodb://localhost:27017/")
db = mongodb_client['iNeuron']
grid_fs = GridFS(db)


@app.route('/add/<path:file_type>', methods=['POST'])
def add(file_type):
    res=""
    if file_type.lower() == "podcast":
        requestName = request.form['name']
        content_type = request.files["file"].content_type

        metadataObj = {
            "name": requestName,
            "duration": request.form['duration'],
            "host": request.form['host'],
            "participants": request.form['participants'].split(",")
        }

        with grid_fs.new_file(file_type=file_type, file_name=requestName, content_type=content_type,
                              metadata=metadataObj) as fp:
            try:
                fp.write(request.files["file"])
                res = fp._id
            finally:
                fp.close()
        if grid_fs.find_one({'_id': res}) is not None:
            return json.dumps({'status': 'File saved successfully'}), 200
        else:
            return json.dumps({'status': 'Error occurred while saving file.'}), 500

    elif file_type.lower() == "song":
        requestName = request.form['name']
        content_type = request.files["file"].content_type

        metadataObj = {
            "name": requestName,
            "duration": request.form['duration']
        }

        with grid_fs.new_file(fileType=file_type, filename=requestName, contentType=content_type,
                              metadata=metadataObj) as fp:

            try:
                fp.write(request.files["file"])
                res = fp._id
            finally:
                fp.close()

        if grid_fs.find_one({'_id': res}) is not None:
            return json.dumps({'status': 'File saved successfully'}), 200
        else:
            return json.dumps({'status': 'Error occurred while saving file.'}), 500

    elif file_type.lower() == "audiobook":
        requestName = request.form['name']
        content_type = request.files["file"].content_type

        metadataObj = {
            "name": requestName,
            "duration": request.form['duration'],
            "author": request.form['author'],
            "narrator": request.form['narrator']
        }

        with grid_fs.new_file(file_type=file_type, file_name=requestName, content_type=content_type,
                              metadata=metadataObj) as fp:
            try:
                fp.write(request.files["file"])
                res= fp._id
            finally:
                fp.close()
        if grid_fs.find_one({'_id': res}) is not None:
            return json.dumps({'status': 'File saved successfully'}), 200
        else:
            return json.dumps({'status': 'Error occurred while saving file.'}), 500
    else:
        return "400"


@app.route('/update/<path:file_type>/<path:file_id>', methods=['PUT'])
def update(file_type, file_id):
    if file_type.lower() == 'song':
        _json = request.json
        _name = _json['name']
        _duration = _json['duration']
        metadataObj = {
            "name": _name,
            "duration": _duration
        }
        db.fs.files.update({'_id': ObjectId(file_id)}, {"$set": {'metadata': metadataObj}})
        return json.dumps({'status': 'File metadata update successfully'}), 200
    elif file_type.lower() == 'podcast':
        _json = request.json
        _name = _json['name']
        _duration = _json['duration']
        _host = _json['host']
        _participants = _json['participants']

        metadataObj = {
            "name": _name,
            "duration": _duration,
            "host": _host,
            "participants": _participants
        }
        db.fs.files.update({'_id': ObjectId(file_id)}, {"$set": {'metadata': metadataObj}})
        return json.dumps({'status': 'File metadata update successfully'}), 200
    elif file_type == 'audiobook':
        _json = request.json
        _name = _json['name']
        _duration = _json['duration']
        _narrator = _json['narrator']
        _author = _json['author']

        metadataObj = {
            "name": _name,
            "duration": _duration,
            "narrator": _narrator,
            "author": _author
        }
        db.fs.files.update({'_id': ObjectId(file_id)}, {"$set": {'metadata': metadataObj}})
        return json.dumps({'status': 'File metadata update successfully'}), 200
    else:
        return "400"


@app.route('/get/<path:file_type>/<path:file_id>')
def index(file_type, file_id):
    grid_fs_file = grid_fs.get(ObjectId(file_id))
    response = make_response(grid_fs_file.read())
    response.headers['Content-Type'] = 'application/octet-stream'

    return response


@app.route('/delete/<path:file_id>', methods=['DELETE'])
def delete(file_id):
    try:
        db['fs.chunks'].remove({'files_id': ObjectId(file_id)})
        db['fs.files'].remove({'_id': ObjectId(file_id)})
        return json.dumps({'status': 'File metadata delete successfully'}), 200
    finally:
        return "200"


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port=8080)
