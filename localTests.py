from OPP.classes.block import BlockClass, BlockIO
import json


input = BlockIO("input", 1)
output = BlockIO("output", 2)

testBlock = BlockClass("test","test","id",[input], [output])
testJson =  testBlock.to_JSON()
print (testJson)


