import sys
import time
import os
from threading import Thread
from pprint import pprint

import requests
import imageio
from win10toast import ToastNotifier


class VirgoolClient:
    class API:
        login = "https://virgool.io/login"  # url1
        user_existence = "https://virgool.io/api/v1.3/auth/user-existence"  # url2
        login_api = "https://virgool.io/api/v1.3/auth/login"  # url3
        notifications = "https://virgool.io/api/v1.3/user/notifications/"  # url4

    def __init__(self):
        self.req = requests.Session()
        self.req.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0"

        if not os.path.isdir('data'):
            os.mkdir("data")

    def login(self, _username: str, _password: str):
        self.req.get(self.API.login)

        self.req.post(self.API.user_existence, data={
            "username": _username,
            "type": "login",
            "method": "username"
        })

        self.req.post(self.API.login_api, data={
            "username": _username,
            "password": _password
        })

    def get_notifs(self, page=1) -> dict:
        return self.req.get(self.API.notifications+str(page)).json()

    def last_update(self, timestamp):
        self.req.post(self.API.notifications, data={"timestamp": timestamp})

    def url_to_image(self, url, avatar) -> str:
        username = url.split("/")[3]

        path = f"data/{username}.png"

        if username not in os.listdir("data"):
            with open(path, 'wb') as f:
                f.write(self.req.get(avatar).content)

            img = imageio.imread(path)
            imageio.imwrite(path.replace(".png", ".ico"), img)

            os.remove(path)

        return path.replace(".png", ".ico")

def arg_parser() -> dict:
    """converts "file.py flag1 value1 flag2 value2" => {flag1:value1, flag2:value2}"""
    args = sys.argv[1:]

    if len(args) % 2 != 0:
        raise Exception("the length of the arguments must be even")

    return {args[i]: args[i+1] for i in range(0, len(args), 2)}


def show_help():
    print(
        "::: Virgool Notifier :::\n\n"
        "use -u <username> -p <password> to login\n"
        "use -t <delay per seconds> to set timeout\n"
        "-----------------------------\n"
    )


def main():
    args = arg_parser()

    delay = float(args.get('-t', '1'))
    username = args.get('-u')
    password = args.get('-p')

    if username is None or password is None:
        show_help()
        raise Exception("information is not enough, enter username & password")

    vir = VirgoolClient()
    vir.login(username, password)

    toaster = ToastNotifier()

    while True:
        time.sleep(delay)

        try:
            data = vir.get_notifs()
        except Exception as err:
            print(err)
            continue

        if data["unread_count"] != 0:
            print(f"have an {data['unread_count']} new messages")

            for i in range(data["unread_count"]):

                toaster.show_toast(
                    title=data["notifications"][i]["notifier_name"],
                    msg=data["notifications"][i]["msg"],
                    icon_path=vir.url_to_image(
                        url=data["notifications"][i]["profile"], avatar=data["notifications"][i]["avatar"]),
                    duration=5)

                vir.last_update(data["notifications"][i]["timestamp"])


if __name__ == "__main__":
    # python vir.py -u username -p password -t delay    
    # python vir.py -u hamidb80 -p mypassrd -t 1.5
    main()
