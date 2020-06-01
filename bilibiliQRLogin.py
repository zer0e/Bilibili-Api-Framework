import requests,qrcode
from urllib import parse
import time,os
from http.cookiejar import MozillaCookieJar
from PIL import Image


class bilibiliQRLogin():
    def __init__(self):
        self.login_session = ''
        self.global_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        self.qr_login_url = 'http://passport.bilibili.com/qrcode/getLoginUrl'
        self.qr_login_info_url = 'http://passport.bilibili.com/qrcode/getLoginInfo'
        self.user_info_url = 'http://account.bilibili.com/home/userInfo'
        self.times = 3 # 超时时间 times*10 秒
        self.cookie_path = './cookie.txt'
        self.qr_path = './qr.png'
        self.load_cookie_from_local()
        if not self.check_expire():
            self.get_login_session()
        
        
        

    def qr_scan(self):
        h = requests.get(self.qr_login_url)

        json_data = h.json()

        oauthKey = json_data['data']['oauthKey']
        qr_image_url = json_data['data']['url']

        # print(oauthKey)
        # print(qr_image_url)

        qr_image = qrcode.make(qr_image_url)
        qr_image.save('qr.png')
        
        return oauthKey


    def get_qr_scan_status(self,oauthKey):
        data = {
            'oauthKey':oauthKey
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        session = requests.Session()
        session.cookies = MozillaCookieJar(self.cookie_path)
        h = session.post(self.qr_login_info_url,headers=headers,data = data)
        status = h.json()['status']
        if status:
            # print(h.text)
            # print(h.headers)
            # print(session.cookies)
            return status,session
        else:
            return status,None

    def check_expire(self):
        if not self.login_session:
            return False
        h = self.login_session.get(self.user_info_url,headers=self.global_headers)
        j = h.json()
        if j['code'] == -101:
            return False
        return True


    def get_login_session(self):
        if self.login_session and self.check_expire():
            return self.login_session
        oauthKey = self.qr_scan()
        print("请扫描二维码")
        img = Image.open(self.qr_path)
        img.show()
        for i in range(self.times):
            time.sleep(10)
            status,session = self.get_qr_scan_status(oauthKey)
            if not status:
                print("等待二维码扫描")
            else:
                print("登录成功")
                self.login_session = session
                self.save_cookie_to_local()
                return session
            if i == self.times - 1:
                print('未扫码超时')
                raise TimeoutError("登录超时")
        return None

    def save_cookie_to_local(self):
        self.login_session.cookies.save(ignore_discard=True, ignore_expires=True)
    
    def load_cookie_from_local(self):
        if os.path.exists(self.cookie_path):
            s = MozillaCookieJar(self.cookie_path)
            s.load(self.cookie_path, ignore_discard=True, ignore_expires=True)
            session = requests.Session()
            session.cookies = s
            self.login_session = session
        else:
            pass
    
    # def test(self):
    #     h = self.login_session.get(self.user_info_url)
    #     print(h.text)








    


if __name__ == "__main__":
    pass
    # l = bilibiliQRLogin()
    # l.test()
    
    







