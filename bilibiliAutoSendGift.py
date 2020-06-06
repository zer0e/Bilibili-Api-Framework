from bilibiliQRLogin import bilibiliQRLogin
from config import logger
import time
from functools import cmp_to_key


class bilibiliAutoSendGift(bilibiliQRLogin):
    def __init__(self):
        super().__init__()
        self.get_medal_url = 'https://api.live.bilibili.com/i/api/medal?page=1&pageSize=10'
        self.get_gift_list_url = "https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list"
        self.bag_send_url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'

    def get_medal_list(self):
        fansMedalList = self.get_login_session().get(self.get_medal_url).json()['data']['fansMedalList']
        newFansMedalList = []
        fansMedalTemplate = {'name':'','uid':'','level':'','medalName':'','dayLimit':'','todayFeed':'','roomId':''}
        for medal in fansMedalList:
            newFansMedal = fansMedalTemplate.copy()
            newFansMedal['name'] = medal['target_name']
            newFansMedal['uid'] = medal['anchorInfo']['uid']
            newFansMedal['level'] = medal['level']
            newFansMedal['medalName'] = medal['medalName']
            newFansMedal['dayLimit'] = medal['dayLimit']
            newFansMedal['todayFeed'] = medal['todayFeed']
            newFansMedal['roomId'] = medal['roomid']
            newFansMedalList.append(newFansMedal)
            # logger.debug(newFansMedal)
        # 按照勋章等级排列
        newFansMedalList.sort(key=cmp_to_key(lambda a,b: b['level'] - a['level']))
        return newFansMedalList
    
    def get_gift_list(self,gitf_id=1):
        # 1为辣条 30607为小心心
        gift_list = self.get_login_session().get(self.get_gift_list_url).json()['data']['list']
        new_gift_list = {'allNum':0,'data': []}
        giftTemplate = {'bag_id':'','gift_id':'','gift_name':'','gift_num':'','expire_at':''}
        for gift in gift_list:
            if gift['gift_id'] != gitf_id:
                continue
            new_gift = giftTemplate.copy()
            for key in new_gift:
                new_gift[key] = gift[key]
            new_gift_list['allNum'] += new_gift['gift_num']
            new_gift_list['data'].append(new_gift)
            # logger.debug(new_gift)
        # 过期时间从小到大排列
        # 事实上官方都排序好了
        new_gift_list['data'].sort(key=cmp_to_key(lambda a,b: a['expire_at'] - b['expire_at']))
        # logger.debug(new_gift_list)
        return new_gift_list
        
    def send_latiao_to_medal(self):
        medal_list = self.get_medal_list()
        gift_list = self.get_gift_list()
        allNum = gift_list['allNum']
        logger.info("当前粉丝勋章有：" + str(medal_list))
        logger.info("当前背包辣条数量：%s",allNum)
        bili_jct = self.get_cookie('bili_jct')
        send_Template = {
            'uid': self.get_cookie('DedeUserID'),
            'csrf': bili_jct,
            'csrf_token': bili_jct,
            'rnd': str(int(time.time())),
            'platform': 'pc',
            'biz_code':'live',
            'storm_beat_id': '0'
        }
        # logger.info(gift_list)
        logger.info("请选择赠送方式：")
        logger.info("1.按粉丝牌等级依次赠送   2.选择粉丝牌等级前两名的主播赠送")
        method = input()
        if method == "2":
            medal_list = medal_list[:2]
        logger.info("当前赠送列表为:" + str(medal_list))
        for medal in medal_list:
            logger.info("将在10秒后开始赠送礼物...")
            time.sleep(10)
            gift_list = self.get_gift_list()
            allNum = gift_list['allNum']
            name = medal['name']
            dayLimit = medal['dayLimit']
            todayFeed = medal['todayFeed']
            ruid = medal['uid']
            biz_id = medal['roomId']
            logger.info("主播名称：%s，今日上限：%s，今日喂食：%s",name,\
                dayLimit,todayFeed)
            
            diff = dayLimit - todayFeed
            if diff > 0:
                logger.info("开始赠送辣条给：%s",name)
                logger.info("当前背包辣条数量：%s",allNum)
                while diff and allNum:
                    gift = gift_list['data'].pop(0)
                    send_gift = send_Template.copy()
                    send_gift['gift_id'] = str(gift['gift_id'])
                    send_gift['gift_num'] = str(gift['gift_num']) if diff > gift['gift_num'] else str(diff)
                    send_gift['bag_id'] = str(gift['bag_id'])
                    send_gift['ruid'] = str(ruid)
                    send_gift['biz_id'] = str(biz_id)
                    diff -= int(send_gift['gift_num'])
                    allNum -= int(send_gift['gift_num'])
                    # logger.info(send_gift)
                    msg = self.get_login_session().post(self.bag_send_url,headers=self.global_headers,data=send_gift).json()
                    # logger.debug(msg)
                    # time.sleep(1000)
                    if msg['msg'] == 'success':
                        logger.info("成功赠送%s个辣条",send_gift['gift_num'])
                        if not allNum or not diff:
                            break
                        logger.info("5秒后开始下一轮送礼")
                        time.sleep(5)
                        continue
                    else:
                        logger.error("未知错误")
                        logger.error(msg)
                        raise Exception("赠送错误")
            else:
                logger.info("主播：%s 今日辣条赠送已达上限",name)
            
            if diff:
                logger.info("背包辣条数量不足，自动跳过剩余主播")
                break
            else:
                logger.info("主播：%s 辣条赠送完毕",name)
        logger.info("结束自动赠送")


if __name__ == "__main__":
    q = bilibiliAutoSendGift()
    # logger.debug(q.get_medal_list())
    
    q.send_latiao_to_medal()

