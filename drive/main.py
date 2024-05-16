from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import glob
import sys
import shutil

from drive.utils import *
from drive.utils_drive import *


class DriveScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.user = None
        self.userType = None
        self.main()

    def main(self):
        main_layout = QHBoxLayout()
        layout1 = QHBoxLayout()
        layout1_ = QVBoxLayout()   
        layout1_ex = QHBoxLayout()     
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()

        button_giris = QPushButton("Giriş")
        button_giris.setMaximumSize(60,40)
        button_upload = QPushButton("Upload")
        button_download = QPushButton("Download")

        button_giris.clicked.connect(self.buttonInput)
        button_upload.clicked.connect(self.buttonUpload)
        button_download.clicked.connect(self.buttonDownload)
        
        self.line = QLineEdit()
        self.label = QLabel()
        self.label_info = QLabel()
        self.label_ = QLabel()

        self.check_layout = QVBoxLayout()
        self.check_layout.addWidget(self.label_info)

        self.label.setText("Giriş Yapınız...")
        self.label.setMaximumSize(210,50)

        self.line.setPlaceholderText("Gmail Hesabınızını giriniz...")
        self.line.setFrame(False)
        self.line.setMaximumSize(200,40)

        self.radio1 = QRadioButton("Users")
        self.radio1.setChecked(True)
        self.radio1.setMaximumSize(60,60)
        self.radio2 = QRadioButton("Admin")
        self.radio2.setEnabled(False)
        self.radio2.setMaximumSize(60,60)
        self.radio2.toggled.connect(self._UserAdmin)

        layout1.addWidget(self.line)
        layout1_ex.addWidget(self.radio1)
        layout1_ex.addWidget(self.radio2)
        layout1_ex.addWidget(button_giris)
        layout1_.addLayout(layout1)
        layout1_.addLayout(layout1_ex)
        layout1_.addWidget(self.label)
        layout1_.addLayout(self.check_layout)

        self.Upload()
        self.Download()

        layout2.addWidget(self.tree_upload)
        layout2.addWidget(button_upload)
        layout3.addWidget(self.tree_dowload)
        layout3.addWidget(button_download)

        main_layout.addLayout(layout1_)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        self.setLayout(main_layout)

        self.starting()
        self.show()

    def starting(self):
        user = startProgram()
        self.__admin_user(user)
        self._UserAdmin()

    def Upload(self):
        self.upload_images_items = dict()
        self.upload_masks_items = dict()

        self.tree_upload = QTreeWidget(self)
        self.tree_upload.setHeaderLabel("Header")

        self.upload_item1 = QTreeWidgetItem()
        self.upload_item1.setText(0,"Images")
        self.upload_item2 = QTreeWidgetItem()
        self.upload_item2.setText(0,"Mask")
        self.tree_upload.addTopLevelItems([self.upload_item1,self.upload_item2])

        self.upload_item1.addChildren(self.upload_images_items.values())
        self.upload_item2.addChildren(self.upload_masks_items.values())

        self.tree_upload.setColumnCount(4)
        self.tree_upload.setHeaderLabels(["Klasör/Dosya","Etiketleyen","Dosya Tipi","Güncelleme Durumu"])

    def Download(self):
        self.dowload_images_items = dict()
        self.dowload_masks_items = dict()

        self.tree_dowload = QTreeWidget(self)
        self.tree_dowload.setHeaderLabel("Header")
        
        self.dowload_item1 = QTreeWidgetItem()
        self.dowload_item1.setText(0,"Images")
        self.dowload_item2 = QTreeWidgetItem()
        self.dowload_item2.setText(0,"Mask")
        self.tree_dowload.addTopLevelItems([self.dowload_item1,self.dowload_item2])

        self.dowload_item1.addChildren(self.dowload_images_items.values())
        self.dowload_item2.addChildren(self.dowload_masks_items.values())

        self.tree_dowload.setColumnCount(4)
        self.tree_dowload.setHeaderLabels(["Klasör/Dosya","Etiketleyen","Dosya Tipi","Yüklenme Durumu"])

    def __admin_user(self,user):
        userType = AdminUsers(user)[0]
        if (userType == "admin"):
            self.user = user
            self.userType = "admin"
            self.label.setText(f"{user}\n Giriş Yapıldı....")
            self.radio2.setEnabled(True)
            self.line.setText(user)
            with open("drive/report/user.txt","w") as f:
                f.write(user)

        elif (userType == "user"):
            self.user = user
            self.userType = "user"
            self.label.setText(f"{user} Giriş Yapıldı....")
            self.line.setText(user)
            self.radio1.setChecked(True)
            self.radio2.setEnabled(False)
            with open("drive/report/user.txt","w") as f:
                f.write(user)
            self._User()
            
        else:
            self.label.setText(AdminUsers(user)[1])
            self.user = None
            self.userType = None,
            self.radio1.setChecked(True)
            self.radio2.setEnabled(False)
            with open("drive/report/user.txt","w") as f:
                f.write("")
            self._User()
        
        self.check_names = []
            
    def buttonInput(self):
        """
            Girilen hesabin var olup olmadığını ve kullanıcı tipini kontrol ediyoruz.
        """
        user = self.line.text()
        self.__admin_user(user)

    def buttonUpload(self):
        print("Upload..............")
        if self.userType == "user":
            user_upload_folder(self.upload_images_items,self.upload_masks_items,self.images_df,self.mask_df)
            self._User()
        elif self.userType == "admin":
            admin_upload_folder(self.check_names,self.upload_images_items,self.upload_masks_items,self.images_df,self.mask_df)
            self.__update_item()
            self.__download_item()

    def buttonDownload(self):
        print("Download.........")
        if self.userType == "user":
            self.dowload_images_items,self.dowload_masks_items = user_download_folder(self.dowload_images_items,self.dowload_masks_items,self.images_df,self.mask_df)
            self._User()
        elif self.userType == "admin":
            self.dowload_images_items,self.dowload_masks_items = admin_download_folder(self.check_names,self.dowload_images_items,self.dowload_masks_items,self.images_df,self.mask_df)
            self.__update_item()
            self.__download_item()

    def _User(self):
        if not(self.user == None):
            self.__update_item()
            self.__download_item()
            string = str(self.user.split("@")[0])
            with open("drive/report/name.txt","w") as f:
                f.write(string)
            f.close()

    def _UserAdmin(self):
        if self.radio1.isChecked():
            self.userType = "user"
            while self.check_layout.count() > 1:
                item = self.check_layout.takeAt(1)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.check_layout.update()
            self._User()
        elif self.radio2.isChecked():
            self.userType = "admin"
            self.checkBox()
            for i in self.check_name_list.values():
                self.check_layout.addWidget(i)

    def checkBox(self):
        with open("drive/report/name.txt","r") as f:
            names = f.read()
        names = names.split("\n")
        self.check_name_list = {}
        for i in admin_Users_read():
            check = QCheckBox(i)
            if i in names:
                check.setChecked(True)
            check.toggled.connect(self.check)
            self.check_name_list[i] = check
        self.check(par=1)

    def __update_item(self):
        while self.upload_item1.childCount() > 0:
            self.upload_item1.takeChild(0)
        while self.upload_item2.childCount() > 0:
            self.upload_item2.takeChild(0)

        self.upload_images_items = dict()
        self.upload_masks_items = dict()

        if self.userType == "user":
            self.upload_images_items,self.upload_masks_items = user_local_folder_read(self.user.split("@")[0],self.upload_images_items,self.upload_masks_items)
        elif self.userType == "admin":
            self.upload_images_items,self.upload_masks_items = admin_local_folder_read(self.check_names,self.upload_images_items,self.upload_masks_items)

        self.upload_item1.addChildren(self.upload_images_items.values())
        self.upload_item2.addChildren(self.upload_masks_items.values())

    def __download_item(self):
        while self.dowload_item1.childCount() > 0:
            self.dowload_item1.takeChild(0)
        while self.dowload_item2.childCount() > 0:
            self.dowload_item2.takeChild(0)

        self.dowload_images_items = dict()
        self.dowload_masks_items = dict()

        if self.userType == "user":
            self.dowload_images_items,self.dowload_masks_items,self.images_df,self.mask_df = user_drive_folder_read(self.user.split("@")[0],self.dowload_images_items,self.dowload_masks_items)
        elif self.userType == "admin":
            self.dowload_images_items,self.dowload_masks_items,self.images_df,self.mask_df = admin_drive_folder_read(self.check_names,self.dowload_images_items,self.dowload_masks_items)

        self.dowload_item1.addChildren(self.dowload_images_items.values())
        self.dowload_item2.addChildren(self.dowload_masks_items.values())

    def check(self,par):
        self.check_names = []
        for i in list(self.check_name_list.keys()):
            if self.check_name_list[i].isChecked():
                self.check_names.append(i)
        self.__update_item()
        self.__download_item()

        string = ""
        for names in self.check_names:
            string += str(names)
            string += "\n"
        with open("drive/report/name.txt","w") as f:
            f.write(string)
        f.close()

    def update_upload(self):
        self.__update_item()
        self.__download_item()

if __name__ == "__main__":
    app = QApplication([])
    window = DriveScreen()
    app.exec()
