from datetime import datetime
from elasticsearch import Elasticsearch
import json
import redis
import random

import pymongo

client = pymongo.MongoClient(host='192.168.2.105', port=27017)

loadGithubDb = client["github2"]
usersColl = loadGithubDb["users2"]

# es = Elasticsearch(["192.168.2.105:9200"])
# es.indices.create(index='logstash-python')
data = 'asd'
# es.index(index="logstash-python",doc_type="test-type",body={"any":"data01","data":json.dumps(data),"timestamp":datetime.now()})

redisclient = redis.Redis(host='127.0.0.1',port=6379,db=0)
tmp = {
    "a":1,
    "b":2
}
redisclient.sadd("hello",tmp)
redisclient.sadd("hello",tmp)

print(redisclient.srandmember("toInsertUser",3))
list = redisclient.srandmember("toInsertUser",3)
readyList = []
for u in list:
    # usersColl.insert_one(json.loads(u))
    print(json.loads(u)["login"])
    readyList.append(json.loads(u))
    #json.loads(u)
    redisclient.srem("toInsertUser",u)
    # print(u["login"])

# redisclient.set("yp","yp")
# print(redisclient.get("lyp")!=None)
# print(type(redisclient.srandmember("toInsertUser",1)))
# redisclient.sadd("toInsertUser2",redisclient.spop("toInsertUser3"))

# for i in range(100):
#     print(random.randint(0,100))

randomInt = random.randint(0, 100)
# progressCondition = {"$or":[{"followingNP": True},{"followerNP":True}],"order":[{"$gt":0},{"$lte":99}]}
progressCondition = {"$or":[{"followingNP": True},{"followerNP":True}]}
print("randomInt:{0}".format(randomInt))
resultList = usersColl.find(progressCondition)
for u in resultList:
    print(u)
    redisclient.sadd("loadTask", u)


