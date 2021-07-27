'''
Author: your name
Date: 2021-07-15 10:05:16
LastEditTime: 2021-07-20 14:25:35
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \pkg\3.py
'''
import gzip
import os
import struct
import zlib

from Crypto import Random
from Crypto.Cipher import AES

"""
aes加密算法
padding : PKCS7
"""

class AESUtil:

    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size

    @staticmethod
    def encryt(string, key, iv):
        """
        加密文本
        :param string: 文本
        :param key: 密钥
        :param iv: 偏移量/初始向量
        :return: 密文
        """
        #print (string)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        x = AESUtil.__BLOCK_SIZE_16 - (len(string) % AESUtil.__BLOCK_SIZE_16)
        # 如果最后一块不够16位需要用字符进行补全
        if x != 0:
            string = string + bytes(chr(x)*x,encoding="utf-8")

        msg = cipher.encrypt(string)
        
        # msg = base64.urlsafe_b64encode(msg).replace('=', '')
        # msg = base64.b64encode(msg)
        return msg

    @staticmethod
    def decrypt(en_str, key, iv):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # en_str += (len(en_str) % 4)*"="
        # decryptByts = base64.urlsafe_b64decode(en_str)
        # decryptByts = base64.b64decode(en_str)
        # msg = cipher.decrypt(decryptByts)

        msg = cipher.decrypt(en_str)
        padding_len = msg[len(msg)-1]
        return msg[0:-padding_len]


def crc32(bytes_obj):
    hashs = 0
    hashs = zlib.crc32(bytes_obj)
    return hashs

def fnv1a_r(oneByte,has):
    return ((oneByte ^ has)*0x1000193) & 0xFFFFFFFF

def getHashCode(data):
    has = 0x811c9dc5
    for i in range(len(data)):
        has = fnv1a_r(data[i],has)
    return has

def gethead(filename,ori_obj,dst_obj):
    ###  ("type_4")
    type_name = b'RBL'
    type_4 = struct.pack('4s',type_name)

    ###  ("fota_algo")
    fota_algo = 258#int(statinfo.st_ctime)
    algo = struct.pack('<H',fota_algo)

    ###  ("ctime")
    statinfo=os.stat(filename)
    
    ctime = int(statinfo.st_mtime)
    ct = struct.pack('<I',ctime)
    ct = b'\x00'*(6-len(ct)) + ct 

    ###  ("app_part_name")
    app_part_name = b'app'
    apn = struct.pack('16s',app_part_name)

    ###  ("download_version")
    download_version  = b'2.0.6'
    dv = struct.pack('24s',download_version)

    ###  ("current_version")
    current_version  = b'00010203040506070809'
    cv = struct.pack('24s',current_version)

    ###  ("body_crc32")
    body_crc32 = struct.pack('<I',crc32(dst_obj))

    ###  ("HASH_CODE")
    hash_val = struct.pack('<I',getHashCode(ori_obj))

    raw_size = len(ori_obj)
    raw_size = struct.pack('<I',raw_size)
    com_size = len(dst_obj)
    com_size = struct.pack('<I',com_size)

    head = type_4 + algo + ct + apn + dv + cv + body_crc32 + hash_val + raw_size + com_size
    head = head + struct.pack('<I',crc32(head))
    return head


if __name__ == "__main__":
    key = b"0123456789ABCDEF0123456789ABCDEF"   # 32位
    iv = b"0123456789ABCDEF"    # 16位
    with open("gzipHeader.bin","rb") as f:
        gzipheader = f.read()
    print ("gzip文件头",gzipheader)
    print ("gzip文件头长度",len(gzipheader))

    #for i in range(96):
    #    print (i,A[i])


    filename = "1.bin"
    with open (filename,"rb") as f:
        bytes_obj = f.read()
        print("加密压缩前文件长度：",len(bytes_obj))
        ### gizp 压缩
        tmp_gizp = gzip.compress(bytes_obj,compresslevel=6)
        tmp = gzipheader + tmp_gizp[10:]
        ### aes 加密
        res = AESUtil.encryt(tmp, key, iv)
        my_head = gethead(filename,bytes_obj,res)
        print (my_head)
        print("加密压缩后文件长度：",len(res))
        
    with open("my_1.rbl","wb") as f:
        f.write(my_head)
        f.write(res)
