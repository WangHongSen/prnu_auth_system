import qrcode
import time
import hashlib
import json
import numpy as np
import prnu
import pickle
from sqlhandler import *
from pyzbar.pyzbar import decode
from PIL import Image

pix_size = 512


def get_info_from_QRcode(QRcode_path):
    #https://github.com/NaturalHistoryMuseum/pyzbar
    encode_data = str(decode(Image.open(QRcode_path))[0][0], encoding = "utf8")
    data = get_decode_data(encode_data)
    if data:     
        data = json.loads(data)        
        return data
    else:
        return None

def get_QRcode(username):
    ticks = time.time()
    username = username
    data = '{"username":"%s","ticks":"%s"}'%(username,ticks)
    
    encode_data = encrypt_data(data)
    save_encode_data_into_db(encode_data,data)
    
    #https://github.com/lincolnloop/python-qrcode
    img = qrcode.make(encode_data)
    img_dir = 'QRcode/'
    #can't save as *.jpg
    img_name = '%s_%s.png'%(ticks,username)
    img_path = img_dir + img_name
    img.save(img_path)

    return img_path

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

    return PCE 

def encrypt_data(data):

    md5 = hashlib.md5()
    md5.update(data.encode("utf8"))
    encrypted_data = md5.hexdigest()
    
    return encrypted_data

def user_authentication_by_password(username,password):
    
    encode_password_in_database = get_password_by_username(username)
    if not encode_password_in_database:
        #Username does not exist!
        return None
    encode_password = encrypt_data(password)
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

    init_db()
    
    path = get_QRcode('test')
    data = get_info_from_QRcode(path)
    print(data['username'])
    
    add_new_user('test','123456')
    img_path_list = ['test/data/myff-jpg/MIX2_WEN_BLANK_HIGH_1.JPG','test/data/myff-jpg/MIX2_WEN_BLANK_HIGH_2.JPG']
    fingerprint = get_fingerprint_from_img_list(img_path_list)
    save_fingerprint_into_db(fingerprint,'test')
    img_path = 'test/data/mynat-jpg/MIX2_WEN_DARK_HIGH_41.JPG'  
    print(user_authentication_by_image('test',img_path))
    print(user_authentication_by_password('test','123456'))
    
if __name__ == "__main__":    
    #print(add_new_user('test','123456'))
    test()
    pass
