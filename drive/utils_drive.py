from drive.Google import Create_Service
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

import os
import io
import pandas as pd
import requests
import json

def download_file_from_google_drive(id, destination):
    URL = "https://drive.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)



try:
    CLIENT_SECRET_FILE = "drive/report/client_secret.json"
    API_NAME = "drive"
    API_VERSION = "v3"
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
except:
    print("hata")
    file = "1UlA8BRTLP9_TdqNe63hraJUVnKnR1f9_"
    destination = "token_drive_v3.pickle"
    download_file_from_google_drive(file,destination)

finally:
    CLIENT_SECRET_FILE = "drive/report/client_secret.json"
    API_NAME = "drive"
    API_VERSION = "v3"
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    

FOLDER_ID = "108mAqo9VToeujX2YzyQTE_74i3QJk38_"
query = f"parents = '{FOLDER_ID}'"


def user_create(UserId):
    file_metadata = {
        "name":UserId,
        "mimeType":"application/vnd.google-apps.folder",
        "parents":[FOLDER_ID]
    }
    created_folder = service.files().create(body=file_metadata).execute()
    created_folder_id = created_folder.get("id")
    image_file_metadata = {
        "name": "images",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [created_folder_id]
    }
    mask_file_metadata = {
        "name": "mask",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [created_folder_id]
    }
    service.files().create(body=image_file_metadata).execute()
    service.files().create(body=mask_file_metadata).execute()

    path = "drive/report"
    file_metadata = {
            "name": "data.json",
            "parents": [created_folder_id]
        }
    media = MediaFileUpload("./{0}/{1}".format(path,"data.json"), mimetype="text/plain")
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    
def admin_Users_read():
    query = f"parents = '{FOLDER_ID}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)
    if df.empty:
        return []
    else:
        return df["name"].to_list()
    
def folder_read(UserId):
    query = f"parents = '{FOLDER_ID}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)

    if df.empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)
    
    if df[df["name"]== UserId].empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)

    folder_id = df[df["name"]== UserId]["id"].values[0]
    query = f"parents = '{folder_id}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)

    image_id = df[df["name"] == "images"]["id"].values[0]
    mask_id = df[df["name"] == "mask"]["id"].values[0]

    query = f"parents = '{image_id}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    images_df = pd.DataFrame(files)

    query = f"parents = '{mask_id}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    masks_df = pd.DataFrame(files)

    return images_df,masks_df

def folder_download(file_id,file_name,folder_type,UserId):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("{0} Dosyası indiliriliyor... {1}".format(file_name,status.progress() * 100))
    fh.seek(0)
    with open(os.path.join("./drive/DataSet/{0}/{1}".format(UserId,folder_type), file_name), "wb") as f:
        f.write(fh.read())
        f.close()

def _folder_id(UserId,folder):
    query = f"parents = '{FOLDER_ID}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)

    Folder_id = df[df["name"] == UserId]["id"].values[0]
    query = f"parents = '{Folder_id}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)
    id = df[df["name"] == folder]["id"].values[0]
    return id

def folder_upload(file_name,mime_type,folder,UserId):
    folder_id = _folder_id(UserId,folder)
    path = f"drive/DataSet/{UserId}/{folder}"

    file_metadata = {
            "name": file_name,
            "parents": [folder_id]
        }
    media = MediaFileUpload("./{0}/{1}".format(path,file_name), mimetype=mime_type)
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

def folder_update(file_name,mime_type,file_id,folder,UserId):
    path = f"drive/DataSet/{UserId}/{folder}"

    file_metadata = {
        "name" : file_name
    }
    media = MediaFileUpload("./{0}/{1}".format(path,file_name), mimetype=mime_type)
    service.files().update(
    fileId=file_id,
    body=file_metadata,
    media_body=media
    ).execute()

def __json_id(UserId):
    query = f"parents = '{FOLDER_ID}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)

    if df.empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)
    
    if df[df["name"]== UserId].empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)

    folder_id = df[df["name"]== UserId]["id"].values[0]
    query = f"parents = '{folder_id}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)
    if df[df["name"] == "data.json"].empty:
        return "json dosyasi yok"
    json_id = df[df["name"] == "data.json"]["id"].values[0]
    return json_id

def _user_id(UserId):
    query = f"parents = '{FOLDER_ID}'"
    response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
    files = response.get("files",[])
    df = pd.DataFrame(files)

    if df.empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)
    
    if df[df["name"]== UserId].empty:
        user_create(UserId)
        query = f"parents = '{FOLDER_ID}'"
        response = service.files().list(q=query,fields='files(kind,mimeType,id,name, modifiedTime)').execute()
        files = response.get("files",[])
        df = pd.DataFrame(files)

    folder_id = df[df["name"]== UserId]["id"].values[0]

    return folder_id

def json_upload_contorl(UserId):
    if __json_id(UserId) == "json dosyasi yok":
        __data_upload(UserId)
    else:
        __data_update(UserId)

def __data_upload(UserId):
    folder_id = _user_id(UserId)
    path = f"drive/DataSet/{UserId}"

    file_metadata = {
            "name": "data.json",
            "parents": [folder_id]
        }
    media = MediaFileUpload("./{0}/{1}".format(path,"data.json"), mimetype="text/plain")
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

def __data_update(UserId):
    json_id = __json_id(UserId)
    path = f"drive/DataSet/{UserId}"
    file_metadata = {
        "name" : "data.json"
    }
    media = MediaFileUpload("./{0}/{1}".format(path,"data.json"), mimetype="text/plain")
    service.files().update(
    fileId=json_id,
    body=file_metadata,
    media_body=media
    ).execute()

def data_download(UserId):
    json_id = __json_id(UserId)
    request = service.files().get_media(fileId=json_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("{0} Dosyası indiliriliyor... {1}".format("data.json",status.progress() * 100))
    fh.seek(0)
    with open(os.path.join("./drive/DataSet/{0}".format(UserId), "data.json"), "wb") as f:
        f.write(fh.read())
        f.close()
