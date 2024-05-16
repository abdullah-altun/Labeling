import json
import os
import glob

from PyQt5.QtWidgets import QTreeWidgetItem

from drive.utils_drive import *

def startProgram():
    if os.path.exists("drive/report/user.txt"):
        with open("drive/report/user.txt","r") as f:
            user = f.read()
        if not(AdminUsers(user)[0] == None):
            return user
        else:
            None
    else:
        return None

def AdminUsers(UsersId):
    with open("drive/report/users.json") as f:
        users = json.load(f)
    
    if UsersId in list(users.keys()):
        return users[UsersId],None
    else:
        text = f"{UsersId} kayitli kullanici değil!!!"
        return None,text

def __folder_create(UserId):
    if not(os.path.exists("drive/DataSet")):
        os.mkdir("drive/DataSet")
    if not(os.path.exists(f"drive/DataSet/{UserId}")):
        os.mkdir(f"drive/DataSet/{UserId}")
        os.mkdir(f"drive/DataSet/{UserId}/images")            
        os.mkdir(f"drive/DataSet/{UserId}/mask")

def __isJson(UserId,name,UserType):
    path = f"drive/DataSet/{UserId}/data.json"
    if UserType == "images":
        if (os.path.exists(path)):
            with open(path,"r") as f:
                data = json.load(f)
            f.close()
            if name in list(data[0].keys()):
                return data[0][name]
            else:
                raise ValueError("Dosya yok!!!")
        else:
            raise ValueError("Json dosyasi yok!!!!!!")
    elif UserType == "mask":
        if (os.path.exists(path)):
            with open(path,"r") as f:
                data = json.load(f)
            f.close()
            if name in list(data[1].keys()):
                return data[1][name]
            else:
                raise ValueError("Dosya yok!!!")
        else:
            raise ValueError("Json dosyasi yok!!!!!!!!!")
        
def user_local_folder_read(UserId,images_items={},mask_items={}):
    __folder_create(UserId)
    def append(folder,folder_items,UserType):
        for name in folder:
            item = QTreeWidgetItem()
            item.setText(0,name)
            item.setText(1,UserId)
            item.setText(2,__isJson(UserId,name,UserType))
            folder_items[name] = item
        return folder_items

    images = glob.glob(f"drive/DataSet/{UserId}/images/**")
    images = [os.path.split(path)[-1] for path in images]
    masks = glob.glob(f"drive/DataSet/{UserId}/mask/**")
    masks = [os.path.split(path)[-1] for path in masks]


    json_control(UserId,images,masks)

    images_items = append(images,images_items,"images")
    mask_items = append(masks,mask_items,"mask")
    return images_items,mask_items

def admin_local_folder_read(UserIds,images_items={},mask_items={}):
    for UserId in UserIds:
        __folder_create(UserId)
        user_local_folder_read(UserId,images_items,mask_items)
    return images_items,mask_items

def user_drive_folder_read(UserId,images_items={},mask_items={}):
    def download_control(UserId,drive_folder,folder_item,folder_type):
        if drive_folder.empty:
            drive_folder = []
        else:
            drive_folder = drive_folder.name.values
        if folder_type == "images":
            local_folder = glob.glob(f"drive/DataSet/{UserId}/images/**")
            local_folder = [os.path.split(path)[-1] for path in local_folder]
            yes_images, no_images = folder_control(local_folder,drive_folder)
            folder_item = append(folder_item,yes_images,no_images)
            return folder_item
        elif folder_type == "mask":
            local_folder = glob.glob(f"drive/DataSet/{UserId}/mask/**")
            local_folder = [os.path.split(path)[-1] for path in local_folder]
            yes_mask, no_mask = folder_control(local_folder,drive_folder)
            folder_item = append(folder_item,yes_mask,no_mask)
            return folder_item
        else:
            raise ValueError("Dosya tipi yanlış!!!!")
        
    def append(folder_items,yes_folder,no_folder):
        for name in yes_folder:
            item = QTreeWidgetItem()
            item.setText(0,name)
            item.setText(1,UserId)
            item.setText(2,"Yüklendi.")
            folder_items[name] = item
        for name in no_folder:
            item = QTreeWidgetItem()
            item.setText(0,name)
            item.setText(1,UserId)
            item.setText(2,"Yüklenmedi...")
            folder_items[name] = item
        return folder_items
    
    def folder_control(local_folder,drive_folder):
        set2 = set(drive_folder)
        set1 = set(local_folder)
        yes_folder = list(set2 & set1)
        no_folder = set2 - set1
        return yes_folder,no_folder

    images_df, mask_df = folder_read(UserId)
    
    __folder_create(UserId)
    images_items = download_control(UserId,images_df,images_items,"images")
    mask_items = download_control(UserId,mask_df,mask_items,"mask")

    return images_items,mask_items,images_df,mask_df

def admin_drive_folder_read(UserIds,images_items={},mask_items={},images_df={},mask_df={}):
    for UserId in UserIds:
        images_items,mask_items,user_img,user_mask = user_drive_folder_read(UserId,images_items,mask_items)
        images_df[UserId] = user_img
        mask_df[UserId] = user_mask
    return images_items,mask_items,images_df,mask_df

def user_download_folder(images_items,mask_items,images_df,mask_df):
    for key in list(images_items.keys()):
        UserId = images_items[key].text(1)
        name = images_items[key].text(0)
        download_type = images_items[key].text(2)
        if download_type == "Yüklendi.":
            pass
        else:
            if images_df[images_df["name"]==name].empty:
                pass
            else:
                id = images_df[images_df["name"]==name].id.values[0]
                folder_download(id,name,"images",UserId)
        
    for key in list(mask_items.keys()):
        UserId = mask_items[key].text(1)
        name = mask_items[key].text(0)
        download_type = mask_items[key].text(2)
        if download_type == "Yüklendi.":
            if mask_df[mask_df["name"]==name].empty:
                pass
            else:
                id = mask_df[mask_df["name"]==name].id.values[0]
                folder_download(id,name,"mask",UserId)
        else:
            if mask_df[mask_df["name"]==name].empty:
                pass
            else:
                id = mask_df[mask_df["name"]==name].id.values[0]
                folder_download(id,name,"mask",UserId) 
        
    data_download(UserId)

    return images_items,mask_items
def userjson(UserId):
    path = f"drive/DataSet/{UserId}/data.json"

    with open(path,"r") as f:
        data = json.load(f)
    f.close()

    def to_change(dicter):
        for key in list(dicter.keys()):
            if (dicter[key] == "Revize edilecek") | (dicter[key] == "Etiketlenecek"):
                dicter[key] =  "Kontrol edilecek"
        
        return dicter
    
    data[0] = to_change(data[0])
    data[1] = to_change(data[1])

    with open(path,"w") as f:
        json.dump(data,f)
    f.close()
    

def admin_download_folder(UserIds,images_items,mask_items,images_df,mask_df):
    for UserId in UserIds:
        images_items,mask_items = user_download_folder(images_items,mask_items,images_df[UserId],mask_df[UserId])
    return images_items,mask_items

def user_upload_folder(images_items,mask_items,images_df,mask_df,UserId_=None,userType="ad"):
    for key in list(images_items.keys()):
        UserId = images_items[key].text(1)
        name = images_items[key].text(0)
        folder_type = images_items[key].text(2)
        upload_type = images_items[key].text(3)
        mime_type = "image/jpeg"

        
        if (UserId_ == None):
            userjson(UserId)

        if upload_type == "Güncel.":
            pass
        else:
            if images_df.empty:
                print(f"{name} dosyası yükleniyor....")
                folder_upload(name,mime_type,"images",UserId) 
            else:
                if (images_df[images_df["name"]==name].empty) & ((UserId_ == None) | (UserId_ == UserId)):
                    print(f"{name} dosyası yükleniyor....")
                    folder_upload(name,mime_type,"images",UserId)

                elif (images_df[images_df["name"]==name].empty):
                    pass
                else:
                    pass
                    # print(f"{name} dosyası güncelleniyor....")
                    # id = images_df[images_df["name"]==name].id.values[0]
                    # folder_update(name,mime_type,id,"images",UserId)

    for key in list(mask_items.keys()):
        UserId = mask_items[key].text(1)
        name = mask_items[key].text(0)
        folder_type = mask_items[key].text(2)
        upload_type = mask_items[key].text(3)
        mime_type = "text/plain"

        if upload_type == "Güncel.":
            pass
        else:
            if mask_df.empty:
                print(f"{name} dosyası yükleniyor....")
                folder_upload(name,mime_type,"mask",UserId) 
            else:
                if (mask_df[mask_df["name"]==name].empty) & ((UserId_ == None) | (UserId_ == UserId)):
                    print(f"{name} dosyası yükleniyor....")
                    folder_upload(name,mime_type,"mask",UserId)
                elif (mask_df[mask_df["name"]==name].empty):
                    pass
                else:
                    print(f"{name} dosyası güncelleniyor....")
                    id = mask_df[mask_df["name"]==name].id.values[0]
                    folder_update(name,mime_type,id,"mask",UserId)
    
    json_upload_contorl(UserId)
    
def admin_upload_folder(UserIds,images_items,mask_items,images_df,mask_df):
    for UserId in UserIds:
        user_upload_folder(images_items,mask_items,images_df[UserId],mask_df[UserId],UserId)

def json_control(UserId,images,masks):
    path = f"drive/DataSet/{UserId}/data.json"
    if not(os.path.exists(path)):
        data = [{},{}]
        with open(path,"w") as f:
            json.dump(data,f)
        f.close()  
    else:
        with open(path,"r") as f:
            data = json.load(f)
        f.close()
    for image in images:
        if image in list(data[0].keys()):
            pass
        else:
            data[0][image] = "Etiketlenecek"

    for mask in masks:
        if mask in list(data[1].keys()):
            pass
        else:
            data[1][mask] = "Etiketlenecek"
    
    with open(path,"w") as f:
        json.dump(data,f)
    f.close()


    

        

    
