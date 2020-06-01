import requests
from bilibiliQRLogin import bilibiliQRLogin

class bilibiliUser(bilibiliQRLogin):
    def __init__(self):
        super().__init__()
        self.all_user_info_url = 'http://api.bilibili.com/nav'
        self.sample_user_info_url = 'http://account.bilibili.com/home/userInfo'
        self.get_location_url = 'http://api.bilibili.com/x/web-interface/zone'
        

    def get_sample_user_info(self):
        return self.get_login_session().get(self.sample_user_info_url).json()

    def get_all_user_info(self):
        return self.get_login_session().get(self.all_user_info_url).json()
    
    def get_location(self):
        return self.get_login_session().get(self.get_location_url).json()

    

if __name__ == "__main__":
    # q = bilibiliQRLogin()
    user = bilibiliUser()
    print(user.get_location())
    
    
    