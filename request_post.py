import random
import re
# import threading
import time
# import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from fake_headers import Headers
import datetime
import logging
logging.basicConfig(filename='crawler.log', level=logging.DEBUG)

# 全部都用selenium 去parse 資訊，不然轉換到soup時，會有問題!!

def setDriver(email,password,fb_main_url=None):
    """_summary_

    Args:
        email (_type_): 登入的帳號
        password (_type_): 登入的密碼
        fb_main_url (_type_, optional): 滑動臉書的初始網址

    Returns:
        _type_: _description_
    """
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    )
    options = Options()
    options.add_argument("--disable-notifications")
    user_agent = header.generate()['User-Agent']
    options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(options=options)
    if fb_main_url != None:
        driver.get(fb_main_url)
        login(driver,email,password, wait_seconds = 10)
    return driver
    
def login(driver,email,password,wait_seconds = 2):
    """_summary_

    Args:
        driver (_type_): 驅動的瀏覽器
        email (_type_): 登入的帳號
        password (_type_): 登入的密碼
        wait_seconds (int, optional): 等待時間跳轉. Defaults to 2.

    Returns:
        _type_: _description_
    """
    try:
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located(("name","email")),
            "Not found"
        )
        # print('find!!')
    except:
        pass
    
    try:
        email_elem = driver.find_element("name","email")
        password_elem = driver.find_element("name","pass")
        email_elem.send_keys(email)
        password_elem.send_keys(password)
        password_elem.submit()
    except:
        pass 
    
    return driver


def clickNext(main_driver,email,password):
    """_summary_

    Args:
        driver (_type_): 驅動的瀏覽器
        email (_type_): 登入的帳號
        password (_type_): 登入的密碼

    Returns:
        _type_: _description_
    """
    # login(main_driver,email,password)
    time.sleep(3.5)
    # //*[@id="m_group_stories_container"]/div/a
    try:
        main_driver.find_element(By.XPATH,'//*[@id="m_group_stories_container"]/div/a').click()
    except Exception as e:
        # print(e)
        logging.error(e)
        # return None
        return False
    return True

def getLink(main_driver,email,password):
    links = []
    main_driver = login(main_driver,email,password)
    time.sleep(3)
    try:
        main_driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    except:
        pass
    try:
        
        WebDriverWait(main_driver, 10).until(
            EC.presence_of_element_located(("id","m_group_stories_container")),
        )
    except:
        return links

    for i in main_driver.find_elements(By.XPATH,'//span[contains(@id,"like_")]'):
        # print(i.get_attribute('id'))
        link = i.find_element(By.TAG_NAME,'a').get_attribute('href')
        links.append(link)

    return links


def requestsPost(driver,url,email,password):
    
    try:
        driver.get(url)
    except:
        return False
    
    driver = login(driver,email,password)
    
    try:
        time_range = random.uniform(3,5)
        WebDriverWait(driver, time_range).until(
            EC.presence_of_element_located(("id","m_story_permalink_view"))
        )
    
    except:
        return False
    
    return True

def getUserName(page_driver,id_):
    # //*[@id="u_0_6_Vm"]/div/header/table/tbody/tr/td[2]/header/h3/strong[1]/a
    # //*[@id="u_0_2_G3"]/div/header/table/tbody/tr/td[2]/header/h3/span/strong[1]/a
    user_name = None
    try:
        # user_name = soup.select_one(f'#{id_} div header table tbody tr').find_all('td')[1].header.h3.span.find_all('strong')[0].a.text
        user_name = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/header/table/tbody/tr/td[2]/header/h3/span/strong[1]/a').text
    except:
        pass
    
    try:
        if user_name == None:
            # user_name = soup.select_one(f'#{id_} div header table tbody tr').find_all('td')[1].header.h3.find_all('strong')[0].a.text
            user_name = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/header/table/tbody/tr/td[2]/header/h3/strong[1]/a').text
    except:
        pass
    
    if user_name != None:
        return user_name
    return "parse name error"
    

def getText(page_driver,id_):
    # //*[@id="u_0_6_St"]/div/div/div/div
    # //*[@id="u_0_6_Ns"]/div/div[1]/div
    # //*[@id="u_0_6_xe"]/div/div[1]/div/p
    text = ""
    try:
        # for t in soup.select_one(f'#{id_}').div.find_all('p'):
        #     try:
        #         text+=t.text
        #     except:
        #         continue
        text = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/div[1]').text
    except:
        pass
    
    if text != "":
        return text
    try:
        page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/div/div/div').text
    except:
        pass
    
    return text

def getImg(page_driver,id_):
    
    
    img_list = []
    try:
        # tree = etree.HTML(str(soup))
        # img_elem = tree.xpath(f'//*[@id="{id_}"]/div/div[2]/div[1]')[0].findall('a')
        # for im in img_elem:
        #     img_list.append(im.find('img').attrib['src'])
        for im in page_driver.find_elements(By.XPATH,f'//*[@id="{id_}"]/div/div[2]/div[1]/a/img'):
            img_list.append(im.get_attribute('src'))
    except:
        pass
    return img_list

def getBlog(page_driver,id_):
    
    try:
        # tree = etree.HTML(str(soup))
        # blog_elem = tree.xpath(f'//*[@id="{id_}"]/div/div[2]/a')[0]#.attrib['href']
        # blog_url = blog_elem.attrib['href']
        # blog_title = tree.xpath(f'//*[@id="{id_}"]/div/div[2]/a/div/table/tbody/tr/td[2]/h3')[0].text
        blog_title = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/div/a/div/table/tbody/tr/td[2]/h3').text
        blog_url = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/div/div/a').get_attribute('href')
        return blog_url,blog_title
    except:
        return None,None

day_name_dict={
    "星期一":0,
    "星期二":1,
    "星期三":2,
    "星期四":3,
    "星期五":4,
    "星期六":5,
    "星期日":6,
}

def parseDate(srt_date):
    try:
        this_year = datetime.datetime.now().year
        if "小時" in srt_date:
            date_obj  = datetime.datetime.today().date()
        if "分鐘" in srt_date:
            date_obj  = datetime.datetime.today().date()
        if "昨天" in srt_date:
            date_obj  = datetime.datetime.today().date()-datetime.timedelta(days=1)
        if "星期" in srt_date:
            week_day = day_name_dict[srt_date[0:3]]
            week_today = datetime.datetime.today().weekday()
            if week_day<week_today:
                minus_day = week_today-week_day
            elif week_day>week_today:
                minus_day = week_today-week_day+7
            times = srt_date[3:]
            date = datetime.datetime.today().date()-datetime.timedelta(days=minus_day)
            date_obj = str(date) + times
                
                
        elif "年" in srt_date:
            if "上午" in srt_date:
                date_obj = datetime.datetime.strptime(srt_date, "%Y年%m月%d日上午%H:%M")
            elif "下午" in srt_date:
                date_obj = datetime.datetime.strptime(srt_date, "%Y年%m月%d日下午%H:%M")
            else:
                date_obj = datetime.datetime.strptime(srt_date, "%Y年%m月%d日")
        else:
            if "上午" in srt_date:
                date_obj = datetime.datetime.strptime(str(this_year) + "年" + srt_date, "%Y年%m月%d日上午%H:%M")
            elif "下午" in srt_date:
                date_obj = datetime.datetime.strptime(str(this_year) + "年" + srt_date, "%Y年%m月%d日下午%H:%M")
        
            
        return str(date_obj)
    except:
        return srt_date

def getDate(page_driver,id_):
    
    srt_date = None
    try:
        # tree = etree.HTML(str(soup))
        # srt_date = tree.xpath(f'//*[@id="{id_}"]/footer/div[1]/abbr')[0].text
        srt_date = page_driver.find_element(By.XPATH,f'//*[@id="{id_}"]/footer/div[1]/abbr').text
        date_obj = parseDate(srt_date)
        return date_obj
    except:
        if srt_date == None:
            return "Timestamp parse error"

def getShortUrl(url):
    url = re.sub(r'refid\S+', '', url, flags=re.MULTILINE).replace('/?','')
    return url
def getLikes(page_driver,comment_id):
    # //*[@id="sentence_2219330364881220"]/a/div/div
    # //*[@id="sentence_2007004656113793"]/a/div/div
    # comment_id = url.replace('https://mbasic.facebook.com/groups/1786425331505061/permalink/','')
    sentiment_id = 'sentence_'+comment_id
    # print(sentiment_id)
    try:
        # //*[@id="sentence_2323278657819723"]/a/div/div
        # tree = etree.HTML(str(soup))
        # likes=tree.xpath(f'//*[@id="{sentiment_id}"]/a/div/div')[0].text
        likes = page_driver.find_element(By.XPATH,f'//*[@id="{sentiment_id}"]/a/div/div').text
    except:
        return "parse likes error"
    
    return likes
def getComment(page_driver,comment_id):
    # //*[@id="ufi_2488276857986568"]/div/div[4]
    # comment_id = url.replace('https://mbasic.facebook.com/groups/1786425331505061/permalink/','')
    uf_id = 'ufi_'+comment_id
    try:
        # tree = etree.HTML(str(soup))
        comments = page_driver.find_elements(By.XPATH,f'//*[@id="{uf_id}"]/div/div[4]/div')
    except:
        return "parse comment error"
    
    c_user_list, c_text_list ,c_date_list = [],[],[]
    for c in comments:
        try:
            c_id = c.get_attribute('id')
            c_user = c.find_element(By.XPATH,f'//*[@id="{c_id}"]/div/h3/a').text
            c_text = c.find_element(By.XPATH,f'//*[@id="{c_id}"]/div/div[1]').text
            c_date = c.find_element(By.XPATH,f'//*[@id="{c_id}"]/div/div[3]/abbr').text
            c_date = parseDate(c_date)
            c_user_list.append(c_user)
            c_text_list.append(c_text)
            c_date_list.append(c_date)
        except:
            continue
    return {
        "comment_user":c_user_list,
        "comment_text":c_text_list,
        "comment_date":c_date_list
    }
def getContent(driver,url,email,password):
    
    url = getShortUrl(url)
    # driver = requestsPost(driver,url,email,password)
    flag = requestsPost(driver,url,email,password)
    if flag == False:
        return {
            'user_name':None,
            'text':None,
            'imgs':None,
            'blog_title':None,
            'blog_url':None,
            'timestamp':None,
            'likes':None,
            'comment':None,
            'memo':"request error"
        }
    
    # //*[@id="viewport"]/div[3]
    time.sleep(random.uniform(6,8))
    
    try:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    except:
        pass
    
    memo = ''
    comment_id = url.replace('https://mbasic.facebook.com/groups/1786425331505061/permalink/','')
    
    # try:
    
    #     WebDriverWait(driver, 3).until(
    #         EC.presence_of_element_located((By.XPATH,f'//*[@id="ufi_{comment_id}"]/div/div[4]'))
    #     )
    # except:
    #     memo = "Timeout: load pages"
    # //*[@id="m_story_permalink_view"]/div/div
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    id_ = driver.find_element(By.XPATH,'//*[@id="m_story_permalink_view"]/div/div').get_attribute('id')
    # id_ = soup.select_one('#m_story_permalink_view').div.div['id']
    
    
    user_name = getUserName(driver,id_)
    text = getText(driver,id_)
    
    imgs = getImg(driver,id_)
    blog_url,blog_title = getBlog(driver,id_)
    timestamp = getDate(driver,id_)
    likes = getLikes(driver,comment_id)
    comment = getComment(driver,comment_id)
    # time.sleep(random.uniform(1,5))
    return {
        'user_name':user_name,
        'text':text,
        'imgs':imgs,
        'blog_title':blog_title,
        'blog_url':blog_url,
        'timestamp':timestamp,
        'likes':likes,
        'comment':comment,
        'memo':memo
    }