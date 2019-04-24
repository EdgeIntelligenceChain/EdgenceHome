from .dep.p2p.Message import Message,Actions
from .dep.p2p.Peer import Peer
from .dep.utils.Utils import Utils

from .dep.ds.Transaction import Transaction
from .dep.ds.Block  import Block
from .dep.ds.TxIn import TxIn
from .dep.ds.TxOut import TxOut
from .dep.ds.MerkleNode import MerkleNode
from .dep.ds.UnspentTxOut import UnspentTxOut
from .dep.ds.OutPoint import OutPoint
from .dep.ds.BlockStats import BlockStats

import binascii
import logging
import os
import socket
import json


logging.basicConfig(
    level=getattr(logging, os.environ.get('TC_LOG_LEVEL', 'INFO')),
    format='[%(asctime)s][%(module)s:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class EdgeExplorerBridge(object):

    def __init__(self, ip:str='127.0.0.1',port:int=9996):

        self.gs = dict()
        self.gs['Block'], self.gs['Transaction'], self.gs['UnspentTxOut'], self.gs['Message'], self.gs['TxIn'], \
            self.gs['TxOut'], self.gs['Peer'], self.gs['OutPoint'],self.gs['BlockStats']= globals()['Block'], globals()['Transaction'], \
            globals()['UnspentTxOut'],globals()['Message'], globals()['TxIn'], globals()['TxOut'], globals()['Peer'], \
                                                                    globals()['OutPoint'],globals()['BlockStats']
        self.peer=Peer(ip,port)
    
    # using socket to get a message,message is the basic transformed data from a 
    # server and a client , this raw data is encoded in json, and can be 
    # de-serilized to an BlockChain Obj. See EdgeHand and EdgeChain for details
    # message Req may be a good idea for debug (linux coreDump) 
    def CliMessageReq(self,message:Message=None)->json:
        if message is None:
            logger.info(f'[EdgeExplorer] a invalid None message')
            raise Exception

        #getting data
        with socket.create_connection(self.peer, timeout=25) as s:
            s.sendall(Utils.encode_socket_data(message))
            msg_len = int(binascii.hexlify(s.recv(4) or b'\x00'), 16)
            data = b''
            while msg_len > 0:
                tdat = s.recv(1024)
                data += tdat
                msg_len -= len(tdat)
        
        return data

    #for a given message request it from the peers and deserilized to it to a obj.
    def CliObjReq(self,message:Message=None)->object:
        data=self.CliMessageReq(message)
        # deserialize to make it to a obj
        retMessage = Utils.deserialize(data.decode(), self.gs) if data else None
        if retMessage is not None:
            logger.info(f"[EdgeExplorer] received a [ {type(retMessage.data).__name__} object ] from peer {self.peer}")
            return retMessage.data
        else:
            logger.info(f'[EdgeExplorer] recv fail for message:{message} from peer {self.peer}')
            return None

    # wapper of those func. to make it capicity to the browser
    # retrun wraped message of a given height block
    def CliBlockReq(self,height:int=1):
        
        try:
            # backend count block at 0 , this is a fix for front end
            retBlock=self.CliObjReq(Message(Actions.BlockAtHeightReq,height-1,123))
        except Exception:
            raise Exception

        logger.info(f'[EdgeExplorer] received [Block]from peer {self.peer}')
        jsonResult={
            'block_header':{
                'height':height,
                'timestamp':retBlock.timestamp,
                'hash':retBlock.id
            },
            'tx_hashes':[]
        }
        txObjResult={}
        for i in retBlock.txns:
            jsonResult['tx_hashes'].append(i.id)
            txObjResult[i.id]=(i,height)
        return jsonResult,txObjResult

    #wrapper for block status    
    def CliBlockStatusReq(self)->json:
        blockStatus=self.CliObjReq(Message(Actions.BlockstatsReq,1,123))
        return {
            'height':blockStatus.height,
            'difficulty':(blockStatus.difficulty.split('.',1)[0]+'.')+(blockStatus.difficulty.split('.',1)[1][:3]),
            'tx_pool_size': blockStatus.tx_pool_size
        }

    #request a list of block data, as usual ,this request is '[lower,upper)' (no upper node)
    def CliBlockReqRange(self,lower:int=1,upper:int=1)->json:
        
        # data validation checks
        height=self.CliBlockStatusReq()['height']
        if height < upper: 
            logger.info(f'[EdgeExplorer] the highest block is {height} , less than {upper}')
            upper=height
        if lower<=0:
            lower=1
        if  lower > upper:
            logger.info(f'[EdgeExplorer] invalid call [upper:{upper},lower:{lower}] {self.peer}')
            #if the var. is too weird,just throw an exception, ～～
            raise Exception
        
        result=[]
        for i in range(lower,upper):
            result.append(self.CliBlockReq(i))
        
        return result
    
        
    def CliTxReq(self,txid:str='',txDict:dict=None)->Transaction:
        if txid in txDict:
            return txDict[txid]
        else:
            logger.info(f'[EdgeExplorer] a invalid txid : {txid}')
    
    def CliTxDataReq(self,txid:str='',txDict:dict=None,blockHeight:int=1):
        (txObj,blockHeight)=self.CliTxReq(txid,txDict)
        return (
            {
                'tx_hash':txObj.id,
                'block_height':blockHeight
            },
            Utils.serialize(txObj)
        )
