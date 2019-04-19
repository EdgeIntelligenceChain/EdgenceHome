import binascii
import time
import json
import hashlib
import threading
import logging
import socketserver
import socket
import random
import os
from functools import lru_cache, wraps
from typing import (
    Iterable, NamedTuple, Dict, Mapping, Union, get_type_hints, Tuple,
    Callable)


from ..ds.UnspentTxOut import UnspentTxOut
from ..ds.OutPoint import OutPoint
from ..ds.Transaction import Transaction

from ..utils.Utils import Utils
from ..params.Params import Params
from ..ds.MerkleNode import MerkleNode
from ..ds.TxIn import TxIn
from ..ds.TxOut import TxOut
from ..params.Params import Params
import _thread


import ecdsa
from base58 import b58encode_check

from _thread import RLock



logging.basicConfig(
    level=getattr(logging, os.environ.get('TC_LOG_LEVEL', 'INFO')),
    format='[%(asctime)s][%(module)s:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class Block(NamedTuple):

    version: int
    prev_block_hash: str
    merkle_hash: str
    timestamp: int
    bits: int
    nonce: int
    txns: Iterable[Transaction]

    def header(self, nonce=None) -> str:
        return (
            f'{self.version}{self.prev_block_hash}{self.merkle_hash}'
            f'{self.timestamp}{self.bits}{nonce or self.nonce}')

    @property
    def id(self) -> str: 
        return Utils.sha256d(self.header())









