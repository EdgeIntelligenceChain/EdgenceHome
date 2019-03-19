## Ubuntu下启动方式

### 1.建立并切换到python虚拟环境

切换到工程目录，执行如下命令进入Python虚拟环境

```
virtualenv --no-site-packages -p /opt/Python3.6.7/bin/python3.6 venv
source venv/bin/activate
```
其中，-p 后的<code>/opt/Python3.6.7/bin/python3.6</code>换成要使用的python解释器在本机的路径。

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
然后，退出交互环境
```
exit()
```

### 4.启动

```
python start.py
```
日志如下：
```
(env) jin@jin-VirtualBox:~/.ssh/EdgenceHome$ python start.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 304-022-857
127.0.0.1 - - [19/Mar/2019 09:34:55] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [19/Mar/2019 09:35:05] "GET /static/favicon.ico HTTP/1.1" 200 -
```
访问网站 http://127.0.0.1:5000/


--------------------------------------------------------------
--------------------------------------------------------------
flask官方文档：http://flask.pocoo.org/docs/1.0/
