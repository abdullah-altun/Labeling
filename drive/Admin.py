import os
import numpy as np
import json

class AdminControl:
    def __init__(self):
        pass

    def json_control(self,folder,folder_type):
        name = folder[0]
        file_type = folder[1]
        UserId = folder[2]
        path = f"drive/DataSet/{UserId}/data.json"
        
        if (os.path.exists(path)):
            with open(path,"r") as f:
                data = json.load(f)
            data[0][name] = folder_type
            name_new = name[:-4] + ".json"
            data[1][name_new] = folder_type

            with open(path,"w") as f:
                json.dump(data,f)
            f.close()

        else:
            raise ValueError("Json Dosyası yokk !!!!!")
        
    def image_file(self,UserId,image_list):
        path = f"drive/DataSet/{UserId}/data.json"
        if (os.path.exists(path)):
            with open(path,"r") as f:
                data = json.load(f)
            for key in list(data[0].keys()):
                if data[0][key] == "Kontrol edildi":
                    pass
                elif data[0][key] == "Kontrol edilecek":
                    pass
                else:
                    image_path = f"drive/DataSet/{UserId}/images/{key}"
                    image_list.append(image_path)
        return image_list
    
    def admin_image_file(self,UserId,image_list):
        path = f"drive/DataSet/{UserId}/data.json"
        if (os.path.exists(path)):
            with open(path,"r") as f:
                data = json.load(f)
            for key in list(data[0].keys()):
                if data[0][key] == "Kontrol edildi":
                    pass              
                else:
                    image_path = f"drive/DataSet/{UserId}/images/{key}"
                    image_list.append(image_path)
        return image_list
        