from bilibiliQRLogin import bilibiliQRLogin


class bilibiliLive(bilibiliQRLogin):
    def __init__(self):
        super().__init__()
        self.live_user_info_url = 'https://api.live.bilibili.com/User/getUserInfo'

    def get_live_user_info(self):
        return self.get_login_session().get(self.live_user_info_url).json()
        

if __name__ == "__main__":
    live =  bilibiliLive()