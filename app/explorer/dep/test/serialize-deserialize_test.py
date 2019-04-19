from EdgeHand import EdgeHand
from dep.utils.Utils import Utils

edgeHand = EdgeHand()

txn = edgeHand.sendTransaction('1NY36FKZqM97oEobfCewhUpHsbzAUSifzo', 0)

txn_serialize = Utils.serialize(txn)

print(txn_serialize)



