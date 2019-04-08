# prnu_auth_system

## 使用方法
克隆项目
`git clone https://github.com/imbawenzi/prnu_auth_system.git`
进入项目目录
`cd prnu_auth_system`
安装依赖
`pip install -r requirements.txt`
运行app.py
`python app.py`

`127.0.0.1:5000/reg`				注册
`127.0.0.1:5000/login`				使用密码登陆
`127.0.0.1:5000/logout`				登出
`127.0.0.1:5000/loginByPRNU`		使用照片登陆
`127.0.0.1:5000/uploadFingerprint`	上传照片

## 文件目录

### images
存放上传的用于生成图片指纹的图片以及用于身份验证的图片

### prnu
存放提取PRNU指纹的函数库

### static/img/QRcode
存放生成的时序的给用户拍摄的二维码

### QRcodeDecoder
存放进行二维码提取以及二维码识别的函数库

### testdata
存放测试数据

### app.py
运行flask,测试样例写在每个函数的上面

### handler.py
存放非数据库操作函数,其中有测试函数test()

### sqlHandler.py
存放数据库操作函数



