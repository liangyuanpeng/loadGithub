from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args
from sgqlc.operation import Operation
import pymongo
import queue
import time
import _thread
# import pylru
import json
import random
import redis

import configparser


class Follower(Type):
    login = str
    avatar_url = str
    isSiteAdmin = bool
    email = str
    updatedAt = str
    name = str
    company = str

class FollowingConnection(Connection):
    nodes = list_of(Follower)

class FollowersConnection(Connection):
    nodes = list_of(Follower)

class User(Type):
    following = Field(FollowingConnection, args=connection_args())
    followers = Field(FollowersConnection, args=connection_args())

class Viewer(Type):
    login = str
    avatar_url = str
    isSiteAdmin = bool
    email = str
    updatedAt = str
    name = str
    company = str


class Query(Type):  # GraphQL's root
    user = Field(User,args={'login':str})
    viewer = Field(Viewer)

def insertData(coll,currentUser,data):
    followingCollList = []
    for i, followerOne in enumerate(data):
        tmpStr = followerOne["name"]
        if tmpStr == "":
            tmpStr = followerOne["login"]

        tmp = {
            "name": tmpStr,
            "email": followerOne["email"],
            "company": followerOne["company"]
        }
        followingCollList.append(tmp)

    if len(followingCollList) > 0:
        followerMap = {
            'user': currentUser,
            'following': followingCollList
        }
        coll.insert_one(followerMap)

def initQueryNodes(object):
    object.nodes.login()
    object.nodes.isSiteAdmin()
    object.nodes.email()
    object.nodes.name()
    object.nodes.updatedAt()
    object.nodes.company()
    object.page_info.__fields__("has_next_page")
    object.page_info.__fields__(end_cursor=True)

def generateGQL(initViewer,currentUser,followingEndCursor,followerEndCursor):
    op = Operation(Query)

    if initViewer:
        viewer = op.viewer()
        viewer.login()
        viewer.isSiteAdmin()
        viewer.email()
        viewer.name()
        viewer.updatedAt()
        viewer.company()

    user = op.user(login=currentUser)
    if followingEndCursor == "":
        following = user.following(first=100)
    elif followingEndCursor == None:
        following = user.following(first=100)
    else:
        following = user.following(first=100,after=followingEndCursor)

    if followerEndCursor == "":
        followers = user.followers(first=100)
    elif followerEndCursor == None:
        followers = user.followers(first=100)
    else:
        followers = user.followers(first=100, after=followerEndCursor)

    initQueryNodes(following)
    initQueryNodes(followers)

    # print(op)
    return op

#插入多条数据，将关注列表以及粉丝列表插入到用户表
def insertListToUser(coll,list):
    # realyList = []
    for index,user in enumerate(list):

        # if user["login"] in userCache:
        if redisclient.get(user["login"]) != None:
            print("######################### {0} in userCache".format(user["login"]))
            continue

        result = coll.find_one({'login': user["login"]})
        # print("-----------------------------------mongo.login:{0}".format(result))
        if result == None:
            user["followingNP"] = True
            user["followerNP"] = True
            user["followingEndCursor"] = ''
            user["followerEndCursor"] = ''
            # realyList.append(user)
            redisclient.sadd("toInsertUser",json.dumps(user))
        # userCache[user["login"]] = 1
        # redisclient.set(user["login"],1)

    # if (len(realyList) > 0):
    #  coll.insert_many(realyList)


def saveOrUpdateProgress(coll,followingNP,followerNP,currentUser, followingEndCursor,followerEndCursor):

    condition = {'login': currentUser}

    result = coll.find_one(condition)

    if result == None:
        print("error")
    else:
        result["followingEndCursor"] = followingEndCursor
        result["followerEndCursor"] = followerEndCursor
        if not followingNP:
            result["followingEndCursor"] = ''
            result["followingNP"] = False
        if not followerNP:
            result["followerEndCursor"] = ''
            result["followerNP"] = False
        if not followingNP:
            if not followerNP:
                # 同时为false，没有后续任务了
                result["order"] = 0
        coll.update(condition, result)

client = pymongo.MongoClient (host = '127.0.0.1' , port = 27017)
loadGithubDb = client["github1"]
usersColl = loadGithubDb["users1"]
followerColl = loadGithubDb["follower1"]
followingColl = loadGithubDb["following1"]
taskQueue = queue.Queue(32)
redisclient = redis.Redis(host='127.0.0.1',port=6379,db=0)

# 方式一
class Settings(object):
    def __init__(self, config_file):
        self.cf = configparser.ConfigParser()
        self.cf.read(config_file)
        for section in self.cf.sections():
    # 读取所有的sections
            for k, v in self.cf.items(section):
        # 读取每个section中的值（key, value）
                setattr(self, k, v)


def initConfig():
    config = configparser.ConfigParser()
    config.read("conf/config.ini")
    settings = Settings("conf/config.ini")
    print(settings.cf.has_option("db","db_name"))
    if config.has_option("redis","redis_host"):
        if config.has_option("redis","redis_port"):
            redisclient = redis.Redis(host=config.get("redis","redis_host"), port=config.getint("redis","redis_port"), db=0)

    if config.has_option("mongo","mongo_host"):
        if config.has_option("mongo","mongo_host"):
            client = pymongo.MongoClient(host=config.get("mongo","mongo_host"), port=config.getint("mongo","mongo_port"))


def main():

    initConfig()

    # Call the endpoint:
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer xxx'}
    endpoint = HTTPEndpoint(url, headers,3)
    taskQueue.put("liangyuanpeng")
    beginReq("liangyuanpeng",True,endpoint,'','')
    progressCondition = {"followingNP":True}
    print(progressCondition)
    _thread.start_new(startInsertUser,())
    _thread.start_new(loadTaskToRedis,())

    while True:
        time.sleep(1)
        task = redisclient.spop("loadTask")
        if task != None:
            print(task)
            one = json.loads(task)
            taskQueue.put(one["login"])
            _thread.start_new_thread(beginReq,(one["login"], False, endpoint, one["followingEndCursor"], one["followerEndCursor"]))

def startInsertUser():
    while True:
        time.sleep(1)
        list = redisclient.srandmember("toInsertUser", 2000)
        print("==================== begin each list.size:{0}".format(len(list)))
        readyList = []
        for u in list:
            jsondata = json.loads(u)
            if redisclient.get("user_"+jsondata["login"]) == None:
                tmp = usersColl.find_one({"login":jsondata["login"]})
                if tmp == None :
                    print("=========================  to add user:{0}".format(jsondata["login"]))
                    jsondata["order"] = random.randint(1,100)
                    readyList.append(jsondata)
                else:
                    print("#################,mongo exist,srem.user:{0}".format(jsondata["login"]))
                    # usersColl.delete_one({"login":jsondata["login"]})
                    redisclient.srem("toInsertUser",u)
                    redisclient.setex("user_" + jsondata["login"], 1, random.randint(2, 4) * 60)
            else:
                print("#################,redis exist,srem.user:{0}".format(jsondata["login"]))
                redisclient.srem("toInsertUser", u)
            # print(json.loads(u)["login"])
        if len(readyList)>0:
            usersColl.insert_many(readyList)

def loadTaskToRedis():
    while True:
        time.sleep(1)
        randomInt = random.randint(1, 100)
        loadTaskCondition = {"$or": [{"followingNP": True}, {"followerNP": True}], "order": {"$lte": randomInt}}
        resultList = usersColl.find(loadTaskCondition)
        print("===================== begin loadTaskCondition :{0}".format(loadTaskCondition))
        for u in resultList:
            redisclient.setex("user_"+u["login"],1,random.randint(2,3)*60)
            if(redisclient.get("task_"+u["login"])) == None:
                u["_id"] = ''
                redisclient.sadd("loadTask",json.dumps(u))
                redisclient.setex("task_"+u["login"],u["login"],random.randint(1,2)*60)

def beginReq(currentUser,doViewer,endpoint,followingEndCursor,followerEndCursor):
    print("begin generateGQL---------------------:{0}".format(currentUser))
    op = generateGQL(doViewer, currentUser,followingEndCursor,followerEndCursor)

    #TODO 请求数据条数
    #TODO 超时不管用
    try:
        # print("do endpoint---------------------:{0},{1},{2}".format(currentUser, taskQueue.qsize(),op))
        print("do endpoint---------------")
        try:
            print(op)
            data = endpoint(op)
            # print(data)
        except Exception as e:
            print("done req {0},op:{1},data:{2}".format(taskQueue.get(),op,json.dumps(data)))
            print(e)
        else:
            print("done endpoint---------------------:{0}".format(currentUser))
            # TODO BUG 报错
            followersList = data.get("data").get("user").get("followers").get("nodes")
            followingList = data.get("data").get("user").get("following").get("nodes")


            if doViewer:
                if redisclient.get(currentUser) == None:
                    tmp = usersColl.find_one({'login': currentUser})
                    if tmp == None:
                        usersColl.insert_one(data.get("data").get("viewer"))

            insertListToUser(usersColl,followersList)
            insertListToUser(usersColl,followingList)

            insertData(followerColl, currentUser, followersList)
            insertData(followingColl, currentUser, followingList)

            haveNextFollowersPage = data.get("data").get("user").get("followers").get("pageInfo").get("hasNextPage")
            haveNextFollowingPage = data.get("data").get("user").get("following").get("pageInfo").get("hasNextPage")

            currentFollowerEndCursor = data.get("data").get("user").get("followers").get("pageInfo").get("endCursor")
            currentFollowingEndCursor = data.get("data").get("user").get("following").get("pageInfo").get("endCursor")

            print("---------------------:{0},{1},{2},{3},{4},{5}".format(currentUser, taskQueue.qsize(),haveNextFollowersPage,currentFollowerEndCursor,haveNextFollowingPage,currentFollowingEndCursor))

            saveOrUpdateProgress(usersColl,haveNextFollowingPage,haveNextFollowersPage, currentUser, currentFollowingEndCursor,currentFollowerEndCursor)

            print("haveNextFollowersPage:{0}".format(haveNextFollowersPage))
            print("haveNextFollowingPage:{0}".format(haveNextFollowingPage))

            print("done req {0}".format(taskQueue.get()))
    except Exception as e:
        print("done req {0}，op:{1},data:{2}".format(taskQueue.get(),op,json.dumps(data)))
        print(e)


if __name__ == '__main__':
    main()