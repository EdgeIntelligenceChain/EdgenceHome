from wallet.Wallet import Wallet
from p2p.Peer import Peer
from p2p.Message import Message
from p2p.Message import Actions
from params import Params
from utils.Utils import Utils
from params.Params import Params

from ds.Transaction import Transaction
from ds.Block  import Block
from ds.TxIn import TxIn
from ds.TxOut import TxOut
from ds.MerkleNode import MerkleNode
from ds.UnspentTxOut import UnspentTxOut
from ds.OutPoint import OutPoint

import os
import time
import random
import socket
import threading
import logging
import argparse
import binascii

from typing import (
    Iterable, NamedTuple, Dict, Mapping, Union, get_type_hints, Tuple,
    Callable)



logging.basicConfig(
    level=getattr(logging, os.environ.get('TC_LOG_LEVEL', 'INFO')),
    format='[%(asctime)s][%(module)s:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class EdgeHand(object):

    def __init__(self, walletFile='mywallet.dat'):

        self.gs = dict()
        self.gs['Block'], self.gs['Transaction'], self.gs['UnspentTxOut'], self.gs['Message'], self.gs['TxIn'], \
            self.gs['TxOut'], self.gs['Peer'], self.gs['OutPoint']= globals()['Block'], globals()['Transaction'], \
            globals()['UnspentTxOut'],globals()['Message'], globals()['TxIn'], globals()['TxOut'], globals()['Peer'], \
                                                                    globals()['OutPoint']

        self.chain_lock = threading.RLock()

        self.wallet = Wallet.init_wallet(walletFile)
        self.peerList = Params.PEERS #Peer.init_peers(Params.PEERS_FILE)

    def _getPort(self)-> Tuple[Peer, int]:
        if self.peerList:
            peerinfo = random.sample(self.peerList, 1)[0]
            peer = Peer(peerinfo[0], peerinfo[1])
        else:
            peer = Peer('127.0.0.1', 9999)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return peer, port

    def _makeTransaction(self, to_addr, value: int = 0, fee: int = 0) -> Transaction:
        utxos_to_spend = set()
        utxos = list(sorted(self.getUTXO4Addr(self.wallet.my_address), key=lambda i: (i.value, i.height)))

        if sum(i.value for i in utxos) < value + fee:
            logger.info(f'[EdgeHand] value to send is larger than balance.')
            return False
        for utxo in utxos:
            utxos_to_spend.add(utxo)
            if sum(i.value for i in utxos_to_spend) > value + fee:
                break
        #print(utxos_to_spend)

        change = sum(i.value for i in utxos_to_spend) - value - fee

        txout = [TxOut(value = value, to_address=to_addr)]
        txout.append(TxOut(value = change, to_address = self.wallet.my_address))
        txin = [self._makeTxin(utxo.outpoint, txout) for utxo in utxos_to_spend]

        txn = Transaction(txins=txin, txouts=txout)

        return txn

    def _makeTxin(self, outpoint: OutPoint, txout: TxOut) -> TxIn:
        sequence = 0
        pk = self.wallet.signing_key.verifying_key.to_string()
        spend_msg = Utils.sha256d(
                    Utils.serialize(outpoint) + str(sequence) +
                    binascii.hexlify(pk).decode() + Utils.serialize(txout)).encode()
        return TxIn(to_spend=outpoint, unlock_pk=pk,
            unlock_sig=self.wallet.signing_key.sign(spend_msg), sequence=sequence)

    def getBalance4Addr(self, wallet_addr: str = None) -> int:
        with self.chain_lock:
            if wallet_addr is None:
                wallet_addr = self.wallet.my_address
            peer, port = self._getPort()
            #print(peer,port)
            message = Message(Actions.Balance4Addr, wallet_addr, port)

            with socket.create_connection(peer, timeout=25) as s:
                s.sendall(Utils.encode_socket_data(message))
                logger.info(f'[EdgeHand] succeed to send Balance4Addr to {peer}')

                msg_len = int(binascii.hexlify(s.recv(4) or b'\x00'), 16)
                data = b''
                while msg_len > 0:
                    tdat = s.recv(1024)
                    data += tdat
                    msg_len -= len(tdat)

                message = Utils.deserialize(data.decode(), self.gs) if data else None
                if message:
                    logger.info(f'[EdgeHand] received Balance4Addr from peer {peer}')
                    return message.data
                else:
                    logger.info(f'[EdgeHand] recv nothing for Balance4Addr from peer {peer}')
                    return None



    def getUTXO4Addr(self, wallet_addr: str = None)-> Iterable[UnspentTxOut]:
        with self.chain_lock:
            if wallet_addr is None:
                wallet_addr = self.wallet.my_address
            peer, port = self._getPort()
            message = Message(Actions.UTXO4Addr, wallet_addr, port)


            with socket.create_connection(peer, timeout=25) as s:
                s.sendall(Utils.encode_socket_data(message))
                logger.info(f'[EdgeHand] succeed to send UTXO4Addr to {peer}')

                msg_len = int(binascii.hexlify(s.recv(4) or b'\x00'), 16)
                data = b''
                while msg_len > 0:
                    tdat = s.recv(1024)
                    data += tdat
                    msg_len -= len(tdat)

                message = Utils.deserialize(data.decode(), self.gs) if data else None
                if message:
                    logger.info(f'[EdgeHand] received UTXO4Addr from peer {peer}')
                    return message.data
                else:
                    logger.info(f'[EdgeHand] recv nothing for UTXO4Addr from peer {peer}')
                    return None



    def sendTransaction(self, to_addr, value):
        with self.chain_lock:
            txn = self._makeTransaction(to_addr, value)
            logger.info(f'[EdgeHand] built txn {txn}')

            peer, port = self._getPort()
            message = Message(Actions.TxRev, txn, port)
            if Utils.send_to_peer(message, peer):
                logger.info(f'[EdgeHand] succeed to send a transaction to {peer}')
                return txn
            else:
                logger.info(f'[EdgeHand] failed to send TxRev to {peer}')
            return None

    def getTxStatus(self, txid: str) -> str:
        with self.chain_lock:
            peer, port = self._getPort()
            message = Message(Actions.TxStatusReq, txid, port)

            with socket.create_connection(peer(), timeout=25) as s:
                s.sendall(Utils.encode_socket_data(message))
                logger.info(f'[EdgeHand] succeed to send TxStatus to {peer}')

                msg_len = int(binascii.hexlify(s.recv(4) or b'\x00'), 16)
                data = b''
                while msg_len > 0:
                    tdat = s.recv(1024)
                    data += tdat
                    msg_len -= len(tdat)

                message = Utils.deserialize(data.decode(), self.gs) if data else None
                if message:
                    logger.info(f'[EdgeHand] received TxStatus from peer {peer}')
                    return message.data
                else:
                    logger.info(f'[EdgeHand] recv nothing for TxStatus from peer {peer}')
                    return None










