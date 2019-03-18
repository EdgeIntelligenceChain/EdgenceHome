## Windows下启动方式

Linux上的部署之后再写

### 1.建立并切换到python虚拟环境

切换到工程目录

```
virtualenv venv
.\venv\Scripts\activate
```

### 2.安装依赖

```
pip install -r requirements.txt
```

### 3.创建数据库

在虚拟环境中输入  

```
python manage.py shell
```

进入交互环境

```
from app.models import db, Role
db.create_all()
Role.insert_roles()
```

数据库创建完成，数据库文件为<code>data-dev.sqlite</code>。

### 4.启动

```
python start.py
```

访问网站 http://127.0.0.1:5000/

### 5. 访问所有界面

右上角有<code>Log In</code>按钮

![](https://ws1.sinaimg.cn/large/7e197809ly1g176184l96j20h40fhaaj.jpg)

点击有注册账户功能。

根据config.py文件中第7行

```py
FLASKY_ADMIN_EMAIL = 'admin@admin.com'
```

注册时若Email为<code>admin@admin.com</code>，则新账户为管理员权限，可以访问所有界面。

--------------------------------------------------------------
--------------------------------------------------------------
flask官方文档：http://flask.pocoo.org/docs/1.0/