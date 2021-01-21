import requests
from pprint import pprint
import time
from threading import Thread
import os
from win10toast import ToastNotifier
import imageio




class Virgool:
    def __init__(self):
        self.req = requests.Session()

        self.username = "Your UserName"
        self.password = "Your Password"


        self.url1 = "https://virgool.io/login"
        self.url2 = "https://virgool.io/api/v1.3/auth/user-existence"
        self.url3 = "https://virgool.io/api/v1.3/auth/login"
        self.url4 = "https://virgool.io/api/v1.3/user/notifications/"
        self.url5 = ""
        self.url6 = ""
        self.url7 = ""

        self.payload1 = {
            "username":self.username,
            "type":"login",
            "method":"username"}

        self.payload2 = {
            "username":self.username,
            "password":self.password
        }

        try:
            os.chdir("data")
            os.chdir("../")
        except:
            os.mkdir("data")


    def login(self):
        req = self.req
        req.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0"
        req.get(self.url1)
        req.post(self.url2,data=self.payload1)
        req.post(self.url3,data=self.payload2)
        self.req = req

    def get_notifs(self,page=1):
        return self.req.get(self.url4+str(page)).json()

    def said_notifs(self,timestamp):
        self.payload3 = {"timestamp":timestamp}
        return self.req.post(self.url4,data=self.payload3)

    def url_to_image(self,url,avatar):
        username = url.split("/")[3]

        path = "data/%s.png" % username
        if username not in os.listdir("data"):
            f = open(path,'wb')
            f.write(self.req.get(avatar).content)
            f.close()
            
            img = imageio.imread(path)
            imageio.imwrite(path.replace(".png",".ico"), img)

            os.remove(path)
        return path.replace(".png",".ico")
    
    

toast = ToastNotifier()


vir = Virgool()
vir.login()
while True:
    time.sleep(0.7)
    data = vir.get_notifs()
    if data["unread_count"] != 0:
        print("have an new messages")
        for i in range(0,data["unread_count"]):
            toast.show_toast(
                title = data["notifications"][i]["notifier_name"],
                msg = data["notifications"][i]["msg"],
                icon_path = vir.url_to_image(url=data["notifications"][i]["profile"],avatar=data["notifications"][i]["avatar"]),
                duration=5)
            vir.said_notifs(data["notifications"][i]["timestamp"])
