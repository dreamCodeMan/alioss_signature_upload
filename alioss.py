# -*- coding: utf-8 -*-

import json
import random
import urlparse
import binascii
import base64
import os
import time
import datetime
import hmac
import hashlib
import crcmod
import requests


def parse_json(url):
    req = requests.get(url)
    dictstr = json.loads(req.text)
    accessid = dictstr['accessid']
    callback = dictstr['callback']
    host = dictstr['host']
    expire = dictstr['expire']
    signature = dictstr['signature']
    policy = dictstr['policy']
    key = dictstr['dir']
    return accessid,callback,host,expire,signature,policy,key

def build_post_body(field_dict, boundary):
    post_body = b''

    for k,v in field_dict.iteritems():
        if k != 'content' and k != 'content-type':
            post_body += '''--{0}\r\nContent-Disposition: form-data; name=\"{1}\"\r\n\r\n{2}\r\n'''.format(boundary, k, v)

    post_body += '''--{0}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{1}\"\r\nContent-Type: {2}\r\n\r\n{3}'''.format(
    boundary, field_dict['key'], field_dict['content-type'], field_dict['content'])

    post_body += '\r\n--{0}--\r\n'.format(boundary)

    return post_body

def build_post_headers(body_len, boundary, headers=None):
    headers = headers if headers else {}
    headers['Content-Length'] = str(body_len)
    headers['Content-Type'] = 'multipart/form-data; boundary={0}'.format(boundary)

    return headers

def calculate_crc64(data):
    _POLY = 0x142F0E1EBA9EA3693
    _XOROUT = 0XFFFFFFFFFFFFFFFF

    crc64 = crcmod.Crc(_POLY, initCrc=0, xorOut=_XOROUT)
    crc64.update(data)

    return crc64.crcValue

signature_url = 'http://oss-demo.aliyuncs.com/oss-h5-upload-js-php-callback/php/get.php'

boundary = hex(int(time.time() * 1000))
accessid,callback,host,expire,signature,policy,key = parse_json(signature_url)

field_dict = {}
field_dict['key'] = key+'test.py'
field_dict['OSSAccessKeyId'] = accessid
field_dict['policy'] = policy
field_dict['success_action_status'] = 200
field_dict['Signature'] = signature
field_dict['callback'] = callback

#上传文件
field_dict['content-type'] = 'application/octet-stream'
f = open('alioss.py', 'rb')
field_dict['content'] = f.read()
f.close()

#上传字符串
#field_dict['content'] = 'a'*64
#field_dict['content-type'] = 'text/plain'

body = build_post_body(field_dict, boundary)
headers = build_post_headers(len(body), boundary)
resp = requests.post(host, data=body, headers=headers)

#检查上传是否完成
assert resp.status_code == 200
assert resp.content == '{"Status":"OK"}'
assert resp.headers['x-oss-hash-crc64ecma'] == str(calculate_crc64(field_dict['content']))

print '{"Status":"OK"}'