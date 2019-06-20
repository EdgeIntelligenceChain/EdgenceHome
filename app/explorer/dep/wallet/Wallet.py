import hashlib
import logging
import os
from functools import lru_cache
import ecdsa
from base58 import b58encode_check

from ..script import scriptBuild

from ..params.Params import Params

logging.basicConfig(
    level=getattr(logging, os.environ.get('TC_LOG_LEVEL', 'INFO')),
    format='[%(asctime)s][%(module)s:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class Wallet(object):

    def __init__(self, signing_key, verifying_key, my_address, keypairs):
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        self.my_address = my_address
        self.keypairs = keypairs

    def __call__(self):
        return self.signing_key, self.verifying_key, self.my_address, self.keypairs

    @classmethod
    def pubkey_to_address(cls, pubkey) -> str:
        try:
            address = scriptBuild.get_address_from_pk(pubkey)
        except Exception as e:
            logger.exception(f"[wallet] Wrong pubkey in generating address with exception {str(e)} ")
            return ''

        return address

    @classmethod
    @lru_cache()
    def init_wallet(cls, path='wallet.dat'):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                signing_key = ecdsa.SigningKey.from_string(
                    f.read(), curve=ecdsa.SECP256k1)
        else:
            logger.info(f"[wallet] generating new wallet: '{path}'")
            signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            with open(path, 'wb') as f:
                f.write(signing_key.to_string())

        verifying_key = signing_key.get_verifying_key()
        my_address = Wallet.pubkey_to_address(verifying_key.to_string())
        logger.info(f"[wallet] your address is {my_address}")

        # get key pairs
        keypairs = []
        key_path = 'keypair'
        if os.path.exists(key_path):
            file_list = os.listdir(key_path)
            for file_name in file_list:
                file_path = key_path + '/' + file_name
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        signing_key = ecdsa.SigningKey.from_string(
                            f.read(), curve=ecdsa.SECP256k1)
                keypairs.append(signing_key)

        # logger.info(f"[wallet] the key pair of the wallet is: '{keypairs}'")
        return cls(signing_key, verifying_key, my_address, keypairs)
