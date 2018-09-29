from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args
from sgqlc.operation import Operation
import pymongo
import queue

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
        # print("{0},{1}".format(i,followerOne))

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
def insertListData(coll,list):
    if(len(list)>0):
        coll.insert_many(list)

taskQueue = queue.Queue(0)

def main():

    # Call the endpoint:
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer xxx'}
    endpoint = HTTPEndpoint(url, headers)
    beginReq("liangyuanpeng",True,endpoint, '', '')

    while True:
        nextUser = taskQueue.get()
        print("---------------------------{0}".format(nextUser))
        beginReq(nextUser, False, endpoint, '', '')


def beginReq(currentUser,doViewer,endpoint,followingEndCursor,followerEndCursor):
    print("beginReq---------------------:{0},{1}".format(currentUser,taskQueue.qsize()))
    # currentUser = "liangyuanpeng"
    # doViewer = True
    op = generateGQL(doViewer, currentUser,followingEndCursor,followerEndCursor)

    #TODO 请求数据条数
    #TODO 翻页有问题 following
    # print("do endpoint---------------------:{0},{1},{2}".format(currentUser, taskQueue.qsize(),op))
    data = endpoint(op)
    print("done endpoint---------------------:{0},{1}".format(currentUser, taskQueue.qsize()))
    followersList = data.get("data").get("user").get("followers").get("nodes")
    followingList = data.get("data").get("user").get("following").get("nodes")

    client = pymongo.MongoClient(host='xxx', port=5917)
    loadGithubDb = client["github"]

    usersColl = loadGithubDb["users"]
    followerColl = loadGithubDb["follower"]
    followingColl = loadGithubDb["following"]
    progressColl = loadGithubDb["progress"]
    if doViewer:
        usersColl.insert_one(data.get("data").get("viewer"))

    # print(followersList)
    # TODO 去重
    insertListData(usersColl,followersList)
    insertListData(usersColl,followingList)

    insertData(followerColl, currentUser, followersList)
    insertData(followingColl, currentUser, followingList)

    haveNextFollowersPage = data.get("data").get("user").get("followers").get("pageInfo").get("hasNextPage")
    haveNextFollowingPage = data.get("data").get("user").get("following").get("pageInfo").get("hasNextPage")

    currentFollowerEndCursor = data.get("data").get("user").get("followers").get("pageInfo").get("endCursor")
    currentFollowingEndCursor = data.get("data").get("user").get("following").get("pageInfo").get("endCursor")

    print("---------------------:{0},{1},{2},{3},{4},{5}".format(currentUser, taskQueue.qsize(),haveNextFollowersPage,currentFollowerEndCursor,haveNextFollowingPage,currentFollowingEndCursor))

    if haveNextFollowersPage :
        tmp = {
            "user":currentUser,
            "type":1,
            "endCursor":currentFollowerEndCursor
        }
        progressColl.insert_one(tmp)
        beginReq(currentUser,doViewer,endpoint,currentFollowingEndCursor,currentFollowerEndCursor)

    if haveNextFollowingPage :
        tmp = {
            "user": currentUser,
            "type": 2,
            "endCursor": currentFollowingEndCursor
        }
        progressColl.insert_one(tmp)
        beginReq(currentUser,doViewer,endpoint,currentFollowingEndCursor,currentFollowerEndCursor)

    # if haveNextFollowersPage:
    print("haveNextFollowersPage:{0}".format(haveNextFollowersPage))
    # if haveNextFollowingPage:
    print("haveNextFollowingPage:{0}".format(haveNextFollowingPage))

    #阻塞了put方法  递归到32  没有get
    for user in followersList:
        print("put {0} in followers queue,queue.size:{1}".format(user["login"],taskQueue.qsize()))
        taskQueue.put(user["login"])
    for user in followingList:
        print("put {0} in following queue,queue.size:{1}".format(user["login"],taskQueue.qsize()))
        taskQueue.put(user["login"])

    # if doViewer:
    #     for user in followersList:
    #         taskQueue.put(user["login"])
    #     for user in followingList:
    #         taskQueue.put(user["login"])
    # else:
    #
    #     if followingEndCursor != "":
    #         if followingEndCursor != None:
    #             for user in followersList:
    #                 taskQueue.put(user["login"])
    #
    #     if followerEndCursor != "":
    #         if followerEndCursor != None:
    #             for user in followingList:
    #                 taskQueue.put(user["login"])

if __name__ == '__main__':
    main()