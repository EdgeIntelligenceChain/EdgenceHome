from EdgeHand import EdgeHand

#初始化钱包,默认本地钱包为mywallet.dat
edgeHand = EdgeHand()

#查询钱包余额，当不传入地址时，默认查询初始化钱包的余额
balance = edgeHand.getBalance4Addr()
print(balance)

utxos = edgeHand.getUTXO4Addr()
if len(utxos) > 0:
    print(f'there are {len(utxos)} utxos for this account')

    txn = edgeHand.sendTransaction('1NY36FKZqM97oEobfCewhUpHsbzAUSifzo', 110)

    txstatus = edgeHand.getTxStatus(txn.id)
    print(txstatus)

#发送交易
#

#print(txn)

#查询交易状态

# 输出样例：
# #185000000000# in address b'1M32gppnnKfCcedHq3weaAagKU7Ppt6KFD'
# #37# utxo in address b'1M32gppnnKfCcedHq3weaAagKU7Ppt6KFD'
# txn 8735269dc5665dea105266ad080a0df003cf3396f9ed296f7f020367f3962ef8 found in_mempool
