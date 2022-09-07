from requests import Session
from bs4 import BeautifulSoup
from execjs import compile
import re
import sys
import json
import datetime

s = Session()
soup = BeautifulSoup()

# 从参数中获取学号和密码
stuID = sys.argv[1]
stuPwd = sys.argv[2]

login_site = s.get('https://wxxy.csu.edu.cn/ncov/wap/default/index')
post_url = login_site.url

soup = BeautifulSoup(markup=login_site.content, features='html.parser')
execution = soup.find(attrs={'id': 'execution'})['value']
pwdEncryptSalt = soup.find(attrs={'id': 'pwdEncryptSalt'})['value']

with open('encrypt.js', 'r', encoding='utf-8') as f:
    js = f.read()
js_compiled = compile(js)
pwd = js_compiled.call(
    'encryptPassword', stuPwd, pwdEncryptSalt)

post_data = {
    'username': stuID,
    'password': pwd,
    'captcha': '',
    '_eventId': 'submit',
    'cllt': 'userNameLogin',
    'dllt': 'generalLogin',
    'lt': '',
    'execution': execution
}

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50'
}

index_site = s.post(url=post_url, data=post_data, headers=header)

content = index_site.text
searchObj = re.search(r'oldInfo: {.*}', content)
if searchObj:
    oldInfo = searchObj.group()
oldInfo = oldInfo.encode('utf-8').decode('unicode_escape')[9:]

searchObj = re.search(r'"geo_api_info":"{.*}",', oldInfo)
if searchObj:
    start = searchObj.start()
    end = searchObj.end()
    geo = searchObj.group()
temp = oldInfo[:start] + oldInfo[end:]
dict = json.loads(temp)
geo = geo.split(':', maxsplit=1)
geo[0] = geo[0][1:-1]
geo[1] = geo[1][1:-2]
dict[geo[0]] = geo[1]
dict['szgjcs'] = ''
dict['gwszdd'] = ''
dict['sfyqjzgc'] = ''
dict['jrsfqzys'] = ''
dict['jrsfqzfy'] = ''
dict['date'] = datetime.datetime.now().strftime('%Y%m%d')

post_url = 'https://wxxy.csu.edu.cn/ncov/wap/default/save'

response = s.post(url=post_url, data=dict, headers=header)

print(response.content.decode('utf-8'))

with open('./GitHub_Action_Results.txt', 'w') as f:
    f.write(f"This was written with a GitHub action")
