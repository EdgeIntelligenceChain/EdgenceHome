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
## Ubuntu下的部署

1. 首先需要安装nginx

```
apt install nginx
```

2. 配置nginx配置文件，之后使用

```
vim /etc/nginx/nginx.conf
```

在http模块中加入如下部分：

```
server {
        listen 80;

        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
}
```

其中，listen后表示监听的端口。之后让nginx重新加载配置文件

```
nginx -s reload
```

使用命令<code>nginx -t</code>检查配置文件是否有错误。

3. 切换到项目目录，启动虚拟环境，使用gunicorn启动flask

```
source venv/bin/activate
```

安装gunicorn

```
pip install gunicorn
```

在后台方式启动gunicorn，保证ssh断开后程序也能正常运行

```
nohup gunicorn -w 4 -b 127.0.0.1:8000 start:app &
```

- -w参数表示启动多少个worker处理网络请求
- -b参数表示将flask app绑定到哪个端口，需要与nginx.conf中的proxy_pass一致

4. 测试访问

在浏览器中直接输入网址 http://45.58.54.216 进行访问，默认端口为nginx.conf中设置的80端口。

若要修改端口，则修改nginx的配置文件并重新加载，在ip后加<code>:port</code>的形式访问。

--------------------------------------------------------------
flask官方文档：http://flask.pocoo.org/docs/1.0/
