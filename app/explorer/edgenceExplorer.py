#!/usr/bin/env python
import json,pickle,pprint,re,time,logging,os
from collections import OrderedDict
from operator import itemgetter
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for,abort
from flask_caching import Cache
import requests

from .Bridge import EdgeExplorerBridge
from config import explorerConfig

from . import explorer
from .. import cache

logging.basicConfig(
    level=getattr(logging, os.environ.get('TC_LOG_LEVEL', 'INFO')),
    format='[%(asctime)s][%(module)s:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)



# a new bridge instance
bridgeInstance=EdgeExplorerBridge(explorerConfig['ip'],explorerConfig['port'])

def is_hex(s):                                         
    result=re.search(r'^[1-9][0-9]*$', s) is not None
    print("\n\n\n\n\n\n\n",result,"/n",s)
    return result


# since the backend is heavyliy proccessing ,and data won't change easily,make it a long cache
@cache.memoize(timeout=6000)
def getBlock(height=1):
    block,txDict=bridgeInstance.CliBlockReq(height)
    try:
        block['block_header']['timestamp'] = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(block['block_header']['timestamp']))
    except:
        block['block_header']['timestamp'] = "Err!"
    return block,txDict



@cache.cached(timeout=60, key_prefix='blockstats')
def blockstats():
    return bridgeInstance.CliBlockStatusReq()

@explorer.errorhandler(404)
@cache.cached(timeout=60)
def error404(e):
    return render_template('404.jinja', page='error',blockstats=blockstats()), 404

@explorer.errorhandler(410)
@cache.cached(timeout=60)
def error410(e):
    return render_template('410.jinja', page='error',blockstats=blockstats()), 410

@explorer.errorhandler(500)
@cache.cached(timeout=60)
def error500(e):
    return render_template('500.jinja', page='error',blockstats=blockstats()), 500



@explorer.route('/block/<block>')
@cache.memoize(timeout=60)
def block(block):
    try:
        blockData,txDict = getBlock(int(block))
    except Exception as e:
        blockData = False
        print(str(e))
        
    return render_template('block.jinja', page='block',blockstats=blockstats(),blockData=blockData)


@explorer.route('/', methods=["GET"])
@cache.cached(timeout=60)
def blockexplorer():
    #We normal just use the function in the render_template, but we need access to the current height.
    stats = blockstats()
    height = stats['height']

    # flask cache is hard to use in test.py 
    # just ... make a copy ~~
    # return a list of (blockInfo,TX_serilized message) tuple
    def inlineGetUpper(lower:int=1,upper:int=1):
        # data validation checks
        if height < upper: 
            logger.info(f'[EdgeExplorer] the highest block is {height} , less than {upper}')
            upper=height
        if lower<=0:
            lower=1
        if  lower > upper:
            logger.info(f'[EdgeExplorer] invalid call [upper:{upper},lower:{lower}] ')
            #if the var. is too weird,just throw an exception, ～～
            raise Exception
        
        result=[]
        for i in range(lower,upper):
            result.append(getBlock(i))
        return result

    blockList=[]
    resultList=inlineGetUpper(height-15,height+1)
    blockList=[block for block,txObj in resultList]

    return render_template('blockexplorer.jinja', page='blockexplorer',blockstats=stats,blockList=blockList)



@explorer.route('/expsearch/', methods=["GET", "POST"])
def expsearch():
    if request.method == 'POST':
        #print(request.form)
        if request.form['blocksearch'] :
            if is_hex(request.form['blocksearch']) and int(request.form['blocksearch'])<int(blockstats()['height']):
                return redirect(url_for('explorer.block', block=request.form['blocksearch']))
            else:
                abort(404)
                return 
        elif request.form['txsearch'] :
            if is_hex(request.form['txsearch']):
                return redirect(url_for('explorer.txid', txid=request.form['txsearch']))
            else:
                abort(404)
                return 
        else:
            abort(404)
            return 
    else:
        return redirect(url_for('explorer.blockexplorer'))



@explorer.route('/block/<blockHeight>/txid/<txid>')
@cache.memoize(timeout=60)
def txid(txid,blockHeight):

    try:
        blockData,txObj=getBlock(int(blockHeight))
        txData=bridgeInstance.CliTxDataReq(txid,txObj,blockData['block_header']['height'])
    except Exception as e:
        txData = (
            {
                'tx_hash':'Err',
                'block_height':'Err'
            },
            {'Err':'Err'}
        )
        print(str(e))

    return render_template('txid.jinja', page='txid',blockstats=blockstats(),txData=txData)



