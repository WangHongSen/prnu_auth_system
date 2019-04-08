import qrcode
import time

import json
import numpy as np
import prnu
import pickle

from QRcodeDecoder import decoder
from glob import glob
from sqlHandler import *

from PIL import Image

pix_size = 2048
QRcode_dir = 'QRcode/'
QRcode_interval = 300

def get_latest_QRcode(username):

    QRcode_list = sorted(glob(QRcode_dir+'*_%s.png'%username))
    if not QRcode_list:
        #no QRcode in dir
        return None,None
    latest_QRcode_path = QRcode_list[-1]
    latest_QRcode_name = latest_QRcode_path.split('/')[-1]
    latest_QRcode_ticks = latest_QRcode_name.split('_')[0]
    
    return latest_QRcode_path,latest_QRcode_ticks
    
def get_info_from_QRcode(QRcode_path):
    #https://github.com/LeonhardFeiner/EasyQrCodeScanner
    encode_data = decoder(QRcode_path)
    data = get_decode_data(encode_data)
    if data:     
        data = json.loads(data)        
        return data
    else:
        return None

def get_QRcode(username):
    
    if not get_password_by_username(username):
        #username does not exist
        return None
    ticks = time.time()
    latest_QRcode_path,latest_QRcode_ticks = get_latest_QRcode(username)
    if latest_QRcode_path:
        if ticks - float(latest_QRcode_ticks) < QRcode_interval:
            return latest_QRcode_path
    
    username = username
    data = '{"username":"%s","ticks":"%s"}'%(username,ticks)
    
    encode_data = hashlib.md5(data.encode("utf8")).hexdigest()
    save_encode_data_into_db(encode_data,data)
    
    #https://github.com/lincolnloop/python-qrcode
    QRcode = qrcode.make(encode_data)
    
    #can't save as *.jpg
    QRcode_name = '%s_%s.png'%(ticks,username)
    QRcode_path = QRcode_dir + QRcode_name
    QRcode.save(QRcode_path)

    return QRcode_path

def get_fingerprint_from_img_list(img_path_list):
    
    imgs = []
    for img_path in img_path_list:
        im = Image.open(img_path)
        im_arr = np.asarray(im)
        if im_arr.dtype != np.uint8:
            print('Error while reading image: {}'.format(img_path))
            continue
        if im_arr.ndim != 3:
            print('Image is not RGB: {}'.format(img_path))
            continue
        im_cut = prnu.cut_ctr(im_arr, (pix_size, pix_size, 3))
        imgs += [im_cut] 
     
    fingerprint = prnu.extract_multiple_aligned(imgs)

    return fingerprint

def get_PCE_from_single_img(fingerprint,img_path):

    img = prnu.cut_ctr(np.asarray(Image.open(img_path)), (pix_size, pix_size, 3))
    detected_fingerprint = prnu.extract_single(img)
    cc2d = prnu.crosscorr_2d(fingerprint, detected_fingerprint)
    PCE = prnu.pce(cc2d)['pce']
    print(PCE)
    return PCE 
    
def user_authentication_by_password(username,password):
    
    encode_password_in_database = get_password_by_username(username)
    if not encode_password_in_database:
        #Username does not exist!
        return None

    encode_password = hashlib.md5(password.encode("utf8")).hexdigest()
    if encode_password == encode_password_in_database:
        return True
    else:
        return False
        #password is not correct
        
def user_authentication_by_image(username,image_path):

    PCEthreshold = 50
    
    fingerprint = get_fingerprint_from_db(username)
    if not fingerprint.any():
        #Username does not exist!
        return None
        
    PCE = get_PCE_from_single_img(fingerprint,image_path)

    if PCE > PCEthreshold:
        return True
    else:
        return False

def test():

    #init_db()
    
    add_new_user('test','123456')
    path = get_QRcode('test')
    data = get_info_from_QRcode(path)
    print(data['username'])
    
    
    img_path_list = ['testdata/MIX2_WEN_BLANK_HIGH_1.JPG','testdata/MIX2_WEN_BLANK_HIGH_2.JPG']
    fingerprint = get_fingerprint_from_img_list(img_path_list)
    save_fingerprint_into_db(fingerprint,'test')
    img_path = 'testdata/test.jpg'  
    print(user_authentication_by_image('test',img_path))
    print(user_authentication_by_password('test','123456'))
    
if __name__ == "__main__":  
    #test()
    pass
