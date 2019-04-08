from flask import Flask

import os
from flask import request, redirect, url_for

from handler import *

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','JPG'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def rename_and_save_file(file):
    #why not use file.save(path) to save file?
    #I use file.read() to get the content of the file to calculate the MD5 of the file.
    #After using file.read(),file.save() will save None.
    #I really don't know why.
    content = file.read()
    filename = hashlib.md5(content).hexdigest()
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    fo = open(path, "wb")
    fo.write(content)
    fo.close()
    return path
    
@app.route('/checkImg', methods=['POST'])
#curl -F "file=@test.jpg; filename=test.jpg" http://127.0.0.1:5000/checkImg
def checkImg():
    if request.method == 'POST':
        file = request.files['file']        
        if file and allowed_file(file.filename):
            img_path = rename_and_save_file(file)
            #todo check for tampering
            data = get_info_from_QRcode(img_path)
            if not data:
                return 'QRcode Invalid!'
            username = data['username']
            ticks = data['ticks']
            '''
            ticks_now = time.time()
            if ticks_now - ticks > 2*QRcode_interval:
                return 'QRcode timeout'
            '''
            result = user_authentication_by_image(username,img_path)
            if result:
                #authentication success
                return 'auth ok'
            else:
                #username does not exist or fingerprint does not match
                return 'auth not ok'            
        else:
            return 'upload file is not image'

@app.route('/uploadFingerprint', methods=['POST'])
#curl -F "photos=@MIX2_WEN_BLANK_HIGH_1.JPG; filename=MIX2_WEN_BLANK_HIGH_1.JPG" -F "photos=@MIX2_WEN_BLANK_HIGH_2.JPG; filename=MIX2_WEN_BLANK_HIGH_2.JPG" http://127.0.0.1:5000/uploadFingerprint
def uploadFingerprint():
    if request.method == 'POST':
        #todo get username
        username = 'test'
        files = request.files.getlist('photos')
        img_path_list = []
        for file in files:
            filename = file.filename
            if file and allowed_file(file.filename):
                img_path = rename_and_save_file(file)
                img_path_list += [img_path]
        #todo check if images is invalid
        fingerprint = get_fingerprint_from_img_list(img_path_list)
        if not save_fingerprint_into_db(fingerprint,username):
            return 'username does not exist'
        return 'ok'
            
            
@app.route('/reg', methods=['POST'])
#curl http://127.0.0.1:5000/reg -X post -d "username=test&password=123456"
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if add_new_user(username,password):
            return 'reg ok'
        else:
            return 'username exists'
      
@app.route('/checkPwd', methods=['POST'])
#curl http://127.0.0.1:5000/check_pwd -X post -d "username=test&password=123456"
def checkPwd():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_authentication_by_password(username,password):
            return 'password correct'
        else:
            return 'password incorrect'
      
@app.route('/getQRcode', methods=['POST'])
#curl http://127.0.0.1:5000/getQRcode -X post -d "username=test"
def getQRcode():
    if request.method == 'POST':
        username = request.form['username']
        path = get_QRcode(username)
        if not path:
            return 'username does not exist'
        return path
        
if __name__ == '__main__':
    app.run(debug=True)
