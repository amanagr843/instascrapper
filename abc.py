from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import requests
import time
import re
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np

class Instalogin():
    def __init__(self,email,password):
        self.browser=webdriver.Chrome("chromedriver2.exe")
        self.email=email
        self.password=password
    def signin(self,user):
        self.browser.get("https://www.instagram.com/accounts/login/")
        time.sleep(1)
        emailinput=self.browser.find_elements_by_css_selector("form input")[0]
        passinput=self.browser.find_elements_by_css_selector("form input")[1]
        emailinput.send_keys(self.email)
        passinput.send_keys(self.password)
        passinput.send_keys(Keys.ENTER)
        time.sleep(10)
        search = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')
        username=user
        search.send_keys(username)
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        search.send_keys(Keys.ENTER)
        time.sleep(6)
        links=[]
        source = self.browser.page_source
        data=bs(source, 'html.parser')
        body = data.find('body')
        script = body.find('span')
        for link in script.findAll('a'):
             if re.match("/p", link.get('href')):
                 links.append('https://www.instagram.com'+link.get('href'))

        results=pd.DataFrame()
        for i in range(len(links)):
            page=urlopen(links[i]).read()
            data=bs(page,"html.parser")
            body=data.find("body")
            script=body.find("script")
            raw=script.text.strip().replace("window._sharedData =","").replace(";","")
            json_data=json.loads(raw)
            posts=json_data['entry_data']['PostPage'][0]['graphql']
            posts=json.dumps(posts)
            posts=json.loads(posts)
            x=pd.DataFrame.from_dict(json_normalize(posts),orient="columns")
            x.columns=x.columns.str.replace("shortcode_media.","")
            results=results.append(x)

        results=results.drop_duplicates(subset="shortcode")
        results.index=range(len(results.index))
        counter=0
        results.to_csv("results.csv")
        for j in range(len(results.index)):
            r=requests.get(results['display_url'][j])
            with open("instaimages/"+str(counter)+".jpeg","wb") as f:
                f.write(r.content)
                counter+= 1
        # print(requests.get(results["owner.profile_pic_url"][0]))
        # with open("profilepic/profile_pic.jpeg","wb") as f1:
        #     f1.write(r1.content)

bot=Instalogin("amanagrwa1804","Cheena@18")
user = input("Enter the target username")
bot.signin(user)
