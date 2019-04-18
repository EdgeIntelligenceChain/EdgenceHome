from flask import render_template
from . import main
import IP2Location
import json
from flask import jsonify


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/masternodes')
def masternodes():
    return render_template('masternodes.html')


@main.route('/getServerInfoList', methods=['GET'])
def getServerInfoList():
    IP2LocObj = IP2Location.IP2Location()
    IP2LocObj.open('./app/static/IP2LOCATION-LITE-DB5.BIN')
    # IPList = ['19.5.10.1', '210.125.84.15', '169.235.24.133', '116.21.94.96']
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
    return json.dumps(res)
