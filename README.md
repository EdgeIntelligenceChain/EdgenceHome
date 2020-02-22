## Ubuntu 下的部署

1. 安装 nginx

```
apt install nginx
```

2. 修改 nginx 配置文件

```
vim /etc/nginx/nginx.conf
```

在http模块中加入如下部分：

```
server {
        listen 80;
        server_name www.edgence.org;
        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
}
```

或者创建 `/etc/nginx/conf.d/www.edgence.org` 文件，填入上述内容。并在 `/etc/nginx/nginx.conf` 文件中添加如下一行：

```
include /etc/nginx/conf.d/www.edgence.org;
```

nginx 重新加载配置文件：

```
nginx -s reload
```

使用命令 `nginx -t` 检查配置文件是否有错误。

3. 切换到项目目录，创建虚拟环境 (需要 Python 3.6 及以上版本：使用了 [f-string](https://www.python.org/dev/peps/pep-0498/) )：

```
# 注：将 python3.6 换为本机上符合版本要求的 python 解释器
python3.6 -m venv venv
```

启动虚拟环境：

```
source venv/bin/activate
```

安装依赖：

```
pip install -r requirements.txt
```

启动 gunicorn：

```
nohup gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfile access.log --error-logfile error.log --reload &
```

- `-w` 参数表示启动多少个 worker 处理网络请求

- `-b` 参数表示将 flask app 绑定到哪个端口，需要与 `nginx.conf` 中的 `proxy_pass` 一致

- `--access-logfile` 与 `--error-logfile` 字段指定了日志文件的保存位置

查看相关进程树，如下分别显示了网站主页EdgenceHome和论坛EdgenceForum这两个进程。
```
root@edgence:~/EdgenceHome# pstree -ap|grep gunicorn
  |-gunicorn,513 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   |-gunicorn,726 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   |-gunicorn,727 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   |-gunicorn,728 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   |-gunicorn,729 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   |-gunicorn,730 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |   `-gunicorn,731 /root/EdgenceHome/venv/bin/gunicorn -w 6 -b 127.0.0.1:8000 start:app --access-logfileaccess.lo
  |-gunicorn,5533 /root/EdgenceForum/.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 wsgi:flaskbb --log-filelogs/gun
  |   |-gunicorn,5539 /root/EdgenceForum/.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 wsgi:flaskbb --log-filelogs/gun
  |   `-gunicorn,5540 /root/EdgenceForum/.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 wsgi:flaskbb --log-filelogs/gun
  |           |-grep,5999 --color=auto gunicorn
root@edgence:~/EdgenceHome# 
```

4. forum 界面对应的安装

见：https://github.com/EdgeIntelligenceChain/EdgenceForum/issues/1#issuecomment-498134553

--------------------------------------------------------------

## Ubuntu 下开发环境启动方式

### 1.建立并切换到 python 虚拟环境

切换到工程目录，执行如下命令进入 python 虚拟环境

```
python3.6 -m venv venv
source venv/bin/activate
```

Python 版本需求 >= 3.6

### 2.安装依赖

```
pip install -r requirements.txt
```

### 3.启动

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

flask官方文档：http://flask.pocoo.org/docs/1.0/
