edgenceExplorer: A Simple Block Explorer for CryptoNote based cryptocurrencies
=========================
* Python 2.7+ is required.
* Python 3.x is likely fine.  In fact, this code is a smaller version of what's running on edgencebase.com - which runs Python 3.5.

**Python External libraries in use:**
* Requests
* Flask
* Flask-Caching 

* Gunicorn, Supervisor, NGINX, and VirtualEnv are suggested.
* Supervisor and NGINX config files are located in the "examples" directory.  
  * There are two supervisor config files - one that just maintains the block explorer - and another that manages a "edgenced" daemon.
  * The example config files assume that you're running in a virtualenv under /srv/edgenceExplorer and using gunicorn to serve the site.
  * The NGINX config may require some tweaking for your site.

To change the default host(127.0.0.1) and port(18081) of the Edgence/CryptoNote daemon, there are variables set in the top of the edgenceExplorer.py file.

Quick Start
==========================

Make sure you have git and virtualenv installed.  On Ubuntu/Debian, these can be installed with 
    sudo apt-get install virtualenv python-virtualenv python3-virtualenv git supervisor

(remove "supervisor" if you are not using it as a process manager)


    cd /srv
    git clone https://github.com/Aerbax/edgenceExplorer
    virtualenv edgenceExplorer
    cd edgenceExplorer
    source bin/activate
    pip install -r requirements.txt

To run the explorer in debug mode, launch it with ./edgenceExplorer.py

To use the supervisor configs, drop the conf file located in the examples directory in /etc/supervisor/conf.d/
    supervisorctl reread
    supervisorctl update

