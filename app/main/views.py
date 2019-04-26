from flask import render_template, url_for, redirect
from . import main
import IP2Location
import json
from flask import jsonify
from flask import make_response


@main.route('/')
def index():
    print(url_for('main.static', filename='1.jpg'))
    return render_template('index.html')


@main.route('/explorer')
def explorer():
    return redirect(url_for("explorer.blockexplorer"))


@main.route('/getServerInfoList', methods=['GET'])
def getServerInfoList():
    IP2LocObj = IP2Location.IP2Location()
    IP2LocObj.open('./app/static/IP2LOCATION-LITE-DB5.BIN')
    # 19.5.10.1
    # 210.125.84.15
    # 169.235.24.133
    # 116.21.94.96
    # IPList = ['47.111.168.213', '47.102.41.81', '47.88.63.126', '161.117.84.146', '39.97.166.176', '47.92.85.186', '45.58.54.216']
    IPList = []
    file1 = open('./app/static/ip.txt')
    for line in file1:
        IPList.append(line.strip())
    file1.close()
    
    res = []
    for ip in IPList:
        loc = IP2LocObj.get_all(ip)
        info = {'country_short': str(loc.country_short, encoding='utf-8'),
                'country_long': str(loc.country_long, encoding='utf-8'),
                'region': str(loc.region, encoding='utf-8'),
                'city': str(loc.city, encoding='utf-8'),
                'latitude': loc.latitude,
                'longitude': loc.longitude}
        res.append(info)
    response = make_response(json.dumps(res))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'    
    resp = json.dumps(res)
    return resp
