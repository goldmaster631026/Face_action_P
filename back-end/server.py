from flask import Flask, Response, request, send_file, jsonify
from io import BytesIO
import json
from flask_cors import CORS
from facial_api.main import main_facial_api
import base64
import gdown
import os
import shutil
import requests
from bs4 import BeautifulSoup

from quantum_onedrive_Folder_latest_P import onedrive_folder_download
from quantum_onedrive_file_latest_P import onedrive_file_download
from quantum_sharepoint_folder_latest_P import sharepoint_folder_download

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
######################################

# Read user list from JSON file
with open('users.json') as f:
    users = json.load(f)['users']

# Authentication function
def authenticate():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    try:
        auth_type, auth_info = auth_header.split(' ')
        if auth_type.lower() != 'basic':
            return False
        decoded = base64.b64decode(auth_info).decode('utf-8')
        username, password = decoded.split(':')
        for user in users:
            if user['username'] == username and user['password'] == password:
                return True
    except:
        return False
    return False 


def eraseFolder():
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and '.' not in f and 'facial_api' not in f and 'image_caption' not in f and 'venv' not in f ]
    for folder in folders:
        shutil.rmtree(folder)

def google_folder_download(video_link):
    gdown.download_folder(video_link, quiet=False)
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and '.' not in f and 'facial_api' not in f and 'image_caption' not in f and 'venv' not in f ]
    os.rename(folders[0], "My_Folder")
    return "Ok"
def other_download(video_link):
    folder_name = "My_Folder"
    os.makedirs(folder_name)
    filename = 'My_Folder/video.mp4'
    gdown.download(video_link, filename,fuzzy = True)
    return "Ok"
    
def sharepoint_file_download(video_link):
    response = requests.get(video_link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('sharepoint.html', 'wb') as f:
            f.write(response.content)
        jsonData = str(soup).split("var g_fileInfo =")[1].split(";")[0]
        with open("sharepoint.json", "w", encoding="utf-8") as file:
            file.write(jsonData)
        result = json.loads(jsonData)
        videoUrl = result["downloadUrl"]
        other_download(videoUrl)
        print('File downloaded successfully')
        return "OK"
    else:
        print('Failed to download file')
        return "Failed"
        
    
    
def download_files(video_link):
    if ("folders" in video_link and "google" in video_link and "drive" in video_link):
        google_folder_download(video_link)
        return "downloaded"
    elif ("sharepoint" in video_link and ":v:" in video_link and "idinnovsas" in video_link):
        sharepoint_file_download(video_link)
        return "Sharepoint"
    elif ("1drv.ms" in video_link and "/f/" in video_link):
        onedrive_folder_download(video_link)
        return "OneDrive Folder"
    elif ("1drv.ms" in video_link and "/v/" in video_link):
        onedrive_file_download(video_link)
        return "OneDrive Folder"
    elif ("idinnovsa" in video_link and "/:f:/" in video_link and "sharepoint" in video_link):
        sharepoint_folder_download(video_link)
        return "OneDrive Folder"
    else:
        other_download(video_link)
        return "Other"
            
@app.route('/')
def index():
    return "hello rote"

@app.route('/api/test', methods = ['GET'])
def Hello():
    app.logger.info("Hello test")
    return 'Hello test'

@app.route('/api/facial_emotion_video', methods=['POST'])
def facial_video_api():    
    # results = []
    if not authenticate():
        return Response('Unauthorized', status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})  
    file = request.files['video']
    video = file.save("facial_api/input/video.mp4")
    results = (main_facial_api("facial_api/input/video.mp4" , 1, 20)) + "\n" "SFEFEEF"
    print (type(results))

    return results


@app.route('/api/facial_emotion_link', methods=['POST'])
def facial_link_api():  
    if not authenticate():
        return Response('Unauthorized', status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})  
    
    eraseFolder()
    
    data = request.get_json()
    video_link = data['videoLink']
    
    download_files(video_link)
    
    folder_path = "My_Folder"
    results = ""
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            print (file_name)
            results = results + file_name + "\n"
            results = results + main_facial_api(f'My_Folder/{file_name}', 5, 20,) + "\n" + "\n"
            
            print(type(results))
            
    # # app.logger.info(video_link)
    

    return results

if __name__ == '__main__':
    # app.run( ssl_context=('eduCBAcert.pem', 'eduCBAkey.pem'))
    app.run(host = '0.0.0.0' ,  debug=True)