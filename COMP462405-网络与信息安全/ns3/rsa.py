# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 19:32:34 2019

@author: 90415
"""

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA

# 伪随机数生成器
random_generator = Random.new().read
# rsa算法生成实例
rsa = RSA.generate(1024, random_generator)
 
# master的秘钥对的生成
private_pem = rsa.exportKey()
 
with open('master-private.pem', 'wb') as f:
  f.write(private_pem)
 
public_pem = rsa.publickey().exportKey()
with open('master-public.pem', 'wb') as f:
  f.write(public_pem)


#%%
import base64
message = b"hello, this is a plian text"
with open('master-public.pem') as f:
    key = f.read()
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    print ('加密后:',cipher_text)



with open('master-private.pem') as f:
    key = f.read()
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.decrypt(base64.b64decode(cipher_text), random_generator)
    print ('解密的原文:',text)


#%%
n = b'This is a test message'
h = SHA.new() 
h.update(n)
print('Hash:',h.hexdigest(),'length:',len(h.hexdigest())*4) 

sign_txt = 'sign.txt'

with open('master-private.pem') as f:
    key = f.read()
    private_key = RSA.importKey(key)
    hash_obj = SHA.new(n)
    signer = Signature_pkcs1_v1_5.new(private_key)
    d = base64.b64encode(signer.sign(hash_obj))

f = open(sign_txt,'wb') 
f.write(d) 
f.close()

with open('master-private.pem') as f:
    key = f.read()
    public_key = RSA.importKey(key) 
    sign_file = open(sign_txt,'r') 
    sign = base64.b64decode(sign_file.read()) 
    h = SHA.new(n)
    verifier = Signature_pkcs1_v1_5.new(public_key)
    print('result:', verifier.verify(h,sign))








