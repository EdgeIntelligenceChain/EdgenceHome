import binascii
import hashlib
from math import log

from base58 import b58decode_check, b58encode_check
from ..params.Params import Params

from . import opcodes


def sizeof(n):
    if n == 0:
        return 1
    return int(log(n, 256)) + 1


def get_address_from_pk(pubkey) -> str:
    if 'ripemd160' not in hashlib.algorithms_available:
        raise RuntimeError('missing ripemd160 hash algorithm')

    def hash_pubkey(data):
        sha = hashlib.sha256(data).digest()
        ripe = hashlib.new('ripemd160', sha).digest()
        return ripe

    if isinstance(pubkey, bytes):
        address = b58encode_check(b'\x00' + hash_pubkey(pubkey))
    elif isinstance(pubkey, list):
        # make redeem script and return P2SH address
        redeem = get_redeem_script(pubkey)
        address = b58encode_check(b'\x05' + hash_pubkey(redeem))
    else:
        raise Exception(f"[wallet] get the wrong pubkey in generating address")

    # print(str(b58encode_check(b'\x00' + ripe)).encode('utf-8'))
    # print(type(b58encode_check(b'\x00' + ripe)))
    address = address if isinstance(address, str) else str(address, encoding="utf-8")
    return address


def get_pk_script(to_addr):
    # decode the address to get the public hash, then add it to the script
    head = b58decode_check(to_addr)[0]
    public_key_hash_de = b58decode_check(to_addr)[1:]
    pk_hash = binascii.hexlify(public_key_hash_de)
    if head == 0:
        return make_pk_script(pk_hash)
    elif head == 5:
        return get_p2sh_script(pk_hash)


def make_pk_script(pk_hash) -> str:

    # just use the P2PKH method
    pubkey_script = Script('OP_DUP OP_HASH160').parse()
    pubkey_script += len(pk_hash).to_bytes(1, 'big')
    pubkey_script += pk_hash
    pubkey_script += Script('OP_EQUALVERIFY OP_CHECKSIG').parse()

    return pubkey_script


def get_redeem_script(pubkeys):

    if len(pubkeys) != Params.P2SH_PUBLIC_KEY:
        raise Exception("Length of the input pubkey is not the same as P2SH_PUBLIC_KEY")

    if Params.P2SH_PUBLIC_KEY < Params.P2SH_VERIFY_KEY:
        raise Exception("numbers of P2SH_PUBLIC_KEY should be larger than P2SH_VERIFY_KEY")

    redeem_script = Script('OP_'+str(Params.P2SH_VERIFY_KEY)).parse()
    for pubkey in pubkeys:
        redeem_script += len(pubkey).to_bytes(1, 'big')
        redeem_script += pubkey
    redeem_script += Script('OP_'+str(Params.P2SH_PUBLIC_KEY)+' OP_CHECKMULTISIG').parse()

    return redeem_script


def get_p2sh_script(p2sh_hash) -> bytes:
    pubkey_script = Script('OP_HASH160').parse()
    pubkey_script += len(p2sh_hash).to_bytes(1, 'big')
    pubkey_script += p2sh_hash
    pubkey_script += Script('OP_EQUAL').parse()

    return pubkey_script


def get_signature_script_without_hashtype(txin_type, signature, invalue) -> bytes:
    """
    this version is just for checking our process is good enough to get the message.

    the invalue is publickey for P2PKH way and redeem script for P2SH way.
    """
    def add_len(sub: bytes) -> bytes:
        return len(sub).to_bytes(sizeof(len(sub)), 'big') + sub

    def add_flag(num: int) -> bytes:
        return num.to_bytes(sizeof(num), 'big')

    if txin_type == 0:
        signature_script = add_len(signature)
        signature_script += add_len(invalue)

    elif txin_type == 1:
        if not isinstance(signature, list):
            raise Exception('The input signature is not list for verifying process')
        signature_script = Script('OP_FALSE').parse()
        for sig in signature:
            signature_script += add_len(sig)
        # put in the redeem script
        cnt = len(invalue)
        if cnt < 76:
            signature_script += add_len(invalue)
        elif 76 <= cnt < 2**8:
            signature_script += add_flag(0x4c) + add_len(invalue)  # OP_PUSHDATA1
        elif 2**8 <= cnt < 2**16:
            signature_script += add_flag(0x4d) + add_len(invalue)  # OP_PUSHDATA2
        elif 2**16 <= cnt < 2**32:
            signature_script += add_flag(0x4e) + add_len(invalue)  # OP_PUSHDATA4
        else:
            raise Exception('Can not add OP_PUSHDATA to the signature script.')
    else:
        raise Exception('Can not get signature here.')

    return signature_script


def get_signature_script(txin_type, signature, pk) -> bytes:
    """
    if we use signature with a hash_type we need to check in our code.
    eg : hash_type = b'\x01' (SIGHASH_ALL)and the final signature is (sig + hash_type) and we need to spilt it out later.
    """
    # add hash_type
    sig = signature + b'\x01'

    return get_signature_script_without_hashtype(txin_type, sig, pk)


class Script:
    """
    This class represents a Bitcoin script.
    """

    def __init__(self, script):
        """
        :param script: The script as a string.
        """
        self.script = script

    def parse(self):
        """
        Parses and serializes a script.

        :return: The serialized script, as bytes.
        """
        # we do the process parse the string here
        element = self.script.split(' ')
        serlized_data = b''
        for i in element:
            if i in opcodes.OPCODE_NAMES:
                op = opcodes.OPCODE_NAMES.index(i)
                serlized_data += op.to_bytes(sizeof(op), 'big')
            else:
                # if there is some hex numbers in the script which are not OPCODE
                try:
                    value = int(i, 16)
                    length = sizeof(value)
                    serlized_data += length.to_bytes(sizeof(length), 'big') + value.to_bytes(sizeof(value), 'big')
                except:
                    raise Exception('Unexpected instruction in script : {}'.format(i))
        return serlized_data
