## Ubuntu下启动方式

### 1.建立并切换到python虚拟环境

切换到工程目录

-p 后的<code>/opt/Python3.6.7/bin/python3.6</code>换成要使用的python解释器的路径

```
virtualenv --no-site-packages -p /opt/Python3.6.7/bin/python3.6 venv
source venv/bin/activate
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


--------------------------------------------------------------
--------------------------------------------------------------
flask官方文档：http://flask.pocoo.org/docs/1.0/