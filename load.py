from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args
from sgqlc.operation import Operation
import pymongo
import queue
import time
import _thread
import pylru

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
    realyList = []
    for index,user in enumerate(list):

        if user["login"] in userCache:
            print("######################### {0} in userCache".format(user["login"]))
            continue

        result = coll.find_one({'login': user["login"]})
        # print("-----------------------------------mongo.login:{0}".format(result))
        if result == None:
            user["followingNP"] = True
            user["followerNP"] = True
            user["followingEndCursor"] = ''
            user["followerEndCursor"] = ''
            userCache[user["login"]] = user["login"]
            realyList.append(user)

    if (len(realyList) > 0):
     coll.insert_many(realyList)

taskQueue = queue.Queue(16)


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
        coll.update(condition, result)

client = pymongo.MongoClient(host='172.18.0.2', port=27017)
# client = pymongo.MongoClient(host='172.17.0.3', port=27017)
loadGithubDb = client["github"]
usersColl = loadGithubDb["users"]
followerColl = loadGithubDb["follower"]
followingColl = loadGithubDb["following"]
taskCache = pylru.lrucache(100)
userCache = pylru.lrucache(10000)

def main():

    # Call the endpoint:
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer xxx'}
    endpoint = HTTPEndpoint(url, headers,3)
    # beginReq("liangyuanpeng",True,endpoint, '', '')
    taskQueue.put("liangyuanpeng")
    beginReq("liangyuanpeng",True,endpoint,'','')
    progressCondition = {"followingNP":True}
    print(progressCondition)


    while True:
        time.sleep(1)
        # result = progressColl.find(progressCondition,limit=1)
        result = usersColl.find(progressCondition, limit=500)
        for one in result:
            print("---------------------------{0}".format(one["login"]))
            #TODO 任务去重
            if one["login"] in taskCache:
                print("######################### {0} in taskCache".format(one["login"]))
                continue
            taskCache[one["login"]] = one["login"]
            taskQueue.put(one["login"])
            _thread.start_new_thread(beginReq,(one["login"], False, endpoint, one["followingEndCursor"], one["followerEndCursor"]))
            # beginReq(one["login"], False, endpoint, one["followingEndCursor"], one["followerEndCursor"])

def beginReq(currentUser,doViewer,endpoint,followingEndCursor,followerEndCursor):
    print("begin generateGQL---------------------:{0}".format(currentUser))
    op = generateGQL(doViewer, currentUser,followingEndCursor,followerEndCursor)

    #TODO 请求数据条数
    #TODO 超时不管用
    try:
        # print("do endpoint---------------------:{0},{1},{2}".format(currentUser, taskQueue.qsize(),op))
        print("do endpoint---------------")
        try:
            data = endpoint(op)
        except Exception as e:
            print("done req {0}".format(taskQueue.get()))
            print(e)
        else:
            print("done endpoint---------------------:{0}".format(currentUser))
            # TODO BUG 报错
            followersList = data.get("data").get("user").get("followers").get("nodes")
            followingList = data.get("data").get("user").get("following").get("nodes")


            if doViewer:
                if currentUser not in userCache:
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
        print("done req {0}，op:{1}".format(taskQueue.get(),op))
        print(e)


if __name__ == '__main__':
    main()