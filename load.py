from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args
from sgqlc.operation import Operation
import json
import pymongo

# Declare types matching GitHub GraphQL schema:
class Issue(Type):
    number = int
    title = str

class IssueConnection(Connection):  # Connection provides page_info!
    nodes = list_of(Issue)

class Repository(Type):
    issues = Field(IssueConnection, args=connection_args())

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
    repository = Field(Repository, args={'owner': str, 'name': str})
    user = Field(User,args={'login':str})
    viewer = Field(Viewer)

def insertData(coll,data):
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

# Generate an operation on Query, selecting fields:
op = Operation(Query)

viewer = op.viewer()
viewer.login()
viewer.isSiteAdmin()
viewer.email()
viewer.name()
viewer.updatedAt()
viewer.company()

currentUser = "liangyuanpeng"
user = op.user(login=currentUser)
followers = user.followers(first=10)
following = user.following(first=10)

# op = Operation(Query)
# viewer = op.viewer()
# viewer.login()
# viewer.isSiteAdmin()
# viewer.email()
# viewer.name()
# viewer.updatedAt()
# viewer.company()


# currentUser = "liangyuanpeng"
# user = op.user(login=currentUser)
# followers = user.followers(first=10)
# following = user.following(first=10,after="Y3Vyc29yOnYyOpKnd3lseWVha84AHWOq")


following.nodes.login()
following.nodes.isSiteAdmin()
following.nodes.email()
following.nodes.name()
following.nodes.updatedAt()
following.nodes.company()
following.page_info.__fields__("has_next_page")
following.page_info.__fields__(end_cursor=True)

followers.nodes.login()
followers.nodes.isSiteAdmin()
followers.nodes.email()
followers.nodes.name()
followers.nodes.updatedAt()
followers.nodes.company()
followers.page_info.__fields__("has_next_page")
followers.page_info.__fields__(end_cursor=True)

#存储方案  用户表，粉丝表，关注表，仓库表，start表，watching表，fork表

# you can print the resulting GraphQL
print(op)

# Call the endpoint:
url = 'https://api.github.com/graphql'
headers = {'Authorization': 'bearer xxx'}
endpoint = HTTPEndpoint(url, headers)
data = endpoint(op)

print(data.get("data").get("user"))
print(data.get("data").get("viewer"))
# print(data.get("data").get("user").get("followers").get("pageInfo"))

# print(data.get("data").get("user").get("followers").get("nodes"))
# followersListStr =json.dumps(data.get("data").get("user").get("followers").get("nodes"))
# print(type(followersListStr))
# followersList = json.loads(followersListStr)
# print(type(followersList))
followersList = data.get("data").get("user").get("followers").get("nodes")
followingList = data.get("data").get("user").get("following").get("nodes")


client = pymongo.MongoClient(host='xxx',port=27017)
loadGithubDb = client["github"]

usersColl = loadGithubDb["users"]
followerColl = loadGithubDb["follower"]
followingColl = loadGithubDb["following"]
usersColl.insert_one(data.get("data").get("viewer"))
if len(followersList) > 0:
    usersColl.insert_many(followersList)
if len(followingList) > 0:
    usersColl.insert_many(followingList)

# followersCollList = []
# for i,followerOne in enumerate(followersList):
#     tmpStr = followerOne["name"]
#     if tmpStr == "":
#         tmpStr = followerOne["login"]
#
#     tmp = {
#         "name":tmpStr,
#         "email":followerOne["email"],
#         "company":followerOne["company"]
#     }
#     followersCollList.append(tmp)
#     # print("{0},{1}".format(i,followerOne))
#
# followingCollList = []
# for i,followerOne in enumerate(followingList):
#     tmpStr = followerOne["name"]
#     if tmpStr == "":
#         tmpStr = followerOne["login"]
#
#     tmp = {
#         "name":tmpStr,
#         "email":followerOne["email"],
#         "company":followerOne["company"]
#     }
#     followingCollList.append(tmp)
#     # print("{0},{1}".format(i,followerOne))
#
#
# if len(followersCollList)>0:
#     followerMap = {
#         'user': currentUser,
#         'following': followersCollList
#     }
#     followerColl.insert_one(followerMap)
#
# if len(followingCollList) > 0:
#     followingMap = {
#         'user' : currentUser,
#         'following' : followingCollList
#     }
#     followingColl.insert_one(followingMap)

insertData(followerColl,followersList)
insertData(followingColl,followingList)

haveNextFollowersPage = data.get("data").get("user").get("followers").get("pageInfo").get("hasNextPage")
haveNextFollowingPage = data.get("data").get("user").get("following").get("pageInfo").get("hasNextPage")

followingEndCursor = data.get("data").get("user").get("followers").get("pageInfo").get("endCursor")
followerEndCursor = data.get("data").get("user").get("following").get("pageInfo").get("endCursor")
# if haveNextFollowersPage:
print("haveNextFollowersPage:{0}".format(haveNextFollowersPage))
# if haveNextFollowingPage:
print("haveNextFollowingPage:{0}".format(haveNextFollowingPage))