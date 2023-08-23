from request_post import *
import pandas as pd
import pygsheets
import threading
import time
import random
import configparser
from request_post import *
import queue

config = configparser.ConfigParser()
config.read('./config.ini')
email = config['fb_account']['email']
passw = config['fb_account']['passw']
result_list = []
post_num = 0

class mainWorker(threading.Thread):
    def __init__(self, Que:queue.Queue()):
        threading.Thread.__init__(self)
        
        self.Que = Que
    def run(self):
        main_driver = setDriver(email,passw,'http://mbasic.facebook.com/groups/1786425331505061')
        url_count = 0
        while url_count<=110:
            links = getLink(main_driver,email,passw)
            if len(links)>0:
                for l in links:
                    sl = getShortUrl(l)
                    
                    url_count+=1
                    self.Que.put((sl,url_count))
                
            else:
                continue
            click_flag = False
            while click_flag==False:
                click_flag=clickNext(main_driver,email,passw)
            print("click the new pages")
            
            
class Worker(threading.Thread):
    def __init__(self, Que:queue.Queue(),sheet_test01):
        threading.Thread.__init__(self)
        # self.result_list = result_list
        self.Que = Que
        self.sheet = sheet_test01
    def getAPost(self,driver,url,cur_point):
        # sing_page_driver = setDriver(email,passw,fb_main_url=None)
    
        # print(url)
        try:
            res = getContent(driver,url,email,passw)
            res['url'] = url
            result_list.append(res)
            # self.saveDataToSheet(res,cur_point+1)
        except Exception as e:
            print(e)
            self.Que.put((url,cur_point))
            
    def saveDataToSheet(self,data:dict,current_point):
        self.sheet.update_value('A'+str(current_point), data['url'])
        self.sheet.update_value('B'+str(current_point), data['user_name'])
        self.sheet.update_value('C'+str(current_point), data['text'])
        self.sheet.update_value('D'+str(current_point), str(data['imgs']))
        self.sheet.update_value('E'+str(current_point), data['blog_title'])
        self.sheet.update_value('F'+str(current_point), data['blog_url'])
        self.sheet.update_value('G'+str(current_point), str(data['comment']))
        self.sheet.update_value('H'+str(current_point), data['timestamp'])
        self.sheet.update_value('I'+str(current_point), data['likes'])
        self.sheet.update_value('J'+str(current_point), data['memo'])
    
            
    def run(self):
        driver = setDriver(email,passw)
        # driver = webdriver.Chrome()
        # driver.get(self.url)
        global post_num
        while (self.Que.qsize() > 0) or (post_num < 100):
            item = self.Que.get()
            
            url = item[0]
            url_c = item[1]
            # url = url.replace("https",'http')
            try:
                self.getAPost(driver,url,url_c)
                post_num+=1
                # print(f'finish {url}')
            except:
                continue
            # time.sleep(random.uniform(3,5))
            
        driver.close()
        
        
# auth_file = "./aqueous-flames-396208-687ba5889c5d.json"
# gc = pygsheets.authorize(service_file = auth_file)
# sheet_url = "https://docs.google.com/spreadsheets/d/1YfT73wC3EhEUt7vNMRN4gPNRbKlcSAs18gFfTq9hhGs/edit#gid=0" 
# sheet = gc.open_by_url(sheet_url)
# sheet_test01 = sheet.worksheet_by_title("threads for posts")


# Que = queue.Queue()
# main_worker = mainWorker(Que)
# main_worker.start()
# # time.sleep(10)
# w_list = []
# for i in range(0,1):
#     w = Worker(Que,sheet_test01)
#     w.start()
#     w_list.append(w)

# main_worker.join()
# for i in w_list:
#     i.join()

# postWorker4.join()
# postWorker5.join()
