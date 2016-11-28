from flask import Flask, abort, request
import json

from functions import create_files, get_all_files, delete_all_files, get_recent_files

app = Flask(__name__)
api_url = '/v1.0'

@app.route(api_url+'/files',methods=['POST'])
def create_file():
  content = request.get_json(silent=True)
  filename = content['filename']
  content = content['content']
  if not filename or not content:
    return "cannot create empty file", 400
  if create_files(filename,content):
    return "HTTP 201 CREATED", 201
  else:
    return "error while creating user", 400

@app.route(api_url+'/files',methods=['GET'])
def get_fileList():
  list = {}
  list["files"] = get_all_files()
  return json.dumps(list), 200

@app.route(api_url+'/files',methods=['PUT'])
def update_user():
  return "HTTP 404 NOT FOUND", 404



@app.route(api_url+'/files',methods=['DELETE'])
def delete_files():

  if delete_all_files():
    return 'HTTP 200 OK', 200
  else:
    return 'ERROR', 200


@app.route(api_url+'/files/recently_created',methods=['POST'])
def func1():
  return "HTTP 404 NOT FOUND", 404

@app.route(api_url+'/files/do_ls',methods=['GET'])
def get_rece_files():
   return get_recent_files()
   


@app.route(api_url+'/files/recently_created',methods=['PUT'])
def func2():
  return "HTTP 404 NOT FOUND", 404


@app.route(api_url+'/files/recently_created',methods=['DELETE'])
def func3():
  return "HTTP 404 NOT FOUND", 404


if __name__ == "__main__":
  app.run(host='0.0.0.0',port=8088,debug='True')
