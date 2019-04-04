from flask import Flask

import os
from flask import request, redirect, url_for
from werkzeug import secure_filename

from handler import *

UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/check_img', methods=['POST'])
def check_img():
    if request.method == 'POST':
        file = request.files['file']        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #todo update filename            
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(img_path)
            
            #todo check for tampering
            data = get_info_from_QRcode(img_path)
            if not data:
                return 'QRcode Invalid!'
            #todo check sequence information
            username = data['username']
            result = user_authentication_by_image(username,img_path)
            if result:
                #authentication success
                return 'ok'
            else:
                #username does not exist or fingerprint does not match
                return 'not ok'            
        else:
            return 'upload file is not image'


if __name__ == '__main__':
    app.run(debug=True)
