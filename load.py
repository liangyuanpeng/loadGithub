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
import threading
import redis
import traceback

import configparser


from concurrent import futures
import time
import grpc
import loadgithub_pb2
import loadgithub_pb2_grpc

import os

# 实现 proto 文件中定义的 GreeterServicer
class Greeter(loadgithub_pb2_grpc.GreeterServicer):
    # 实现 proto 文件中定义的 rpc 调用
    def SayHello(self, request, context):
        return loadgithub_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))

    def SayHelloAgain(self, request, context):
        return loadgithub_pb2.HelloReply(message='hello {msg}'.format(msg = request.name))

# class GithubLoader(loadgithub_pb2_grpc.GithubLoaderServicer){
#     def QueryFollow(self,request,context):
#         return loadgithub_pb2.QueryFollowResp()
# }

def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    loadgithub_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    # loadgithub_pb2_grpc.add_GithubLoaderServicer_to_server(GithubLoader(),server)
    #[::]
    server.add_insecure_port('[::]:50051')
    print("grpc starting!!!!!!")
    server.start()
    try:
        while True:
            time.sleep(60*60*24) # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)
        

class Follower(Type):
    login = str
    avatar_url = str
    isSiteAdmin = bool
    email = str
    updatedAt = str
    name = str
    company = str
    createdAt = str

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
    createdAt = str


class Query(Type):  # GraphQL's root
    user = Field(User,args={'login':str})
    viewer = Field(Viewer)

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

    return op
   
def beginReq(currentUser,doViewer,token,followingEndCursor,followerEndCursor):
    print("begin generateGQL---------------------:{0}".format(currentUser))
    op = generateGQL(doViewer, currentUser,followingEndCursor,followerEndCursor)
    
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer '+token}
    endpoint = HTTPEndpoint(url, headers,3)

    #TODO 请求数据条数
    #TODO 超时不管用
    try:
        # print("do endpoint---------------------:{0},{1},{2}".format(currentUser, taskQueue.qsize(),op))
        print("do endpoint---------------")
        try:
            print(op)
            data = endpoint(op)
            # print("endpoint.result.data:"+data)
        except Exception as e:
            print("done op:{0},data:{1}".format(op,json.dumps(data)))
            print(e)
        else:
            # json2python = json.loads(str)
            
            # print(res)
            
            resp = loadgithub_pb2.QueryFollowResp()
            
            # resp = loadgithub_pb2.QueryFollowResp(data=res)
            # print(resp)
            
            # print("done endpoint---------------------:{0}".format(currentUser))
            followersList = data.get("data").get("user").get("followers").get("nodes")
            followingList = data.get("data").get("user").get("following").get("nodes")

            followers = loadgithub_pb2.Follow()
            following = loadgithub_pb2.Follow()

            for item in followersList:
                print(item)
                node = resp.data.user.followers.nodes.add()
                node.login = item.get("login")
                node.isSiteAdmin = item.get("isSiteAdmin")
                email = ""
                if item.get("email") != None:
                    email = item.get("email")
                node.email = email
                name = ""
                if item.get("name") != None:
                    name = item.get("name")
                node.name = name
                node.updatedAt = item.get("updatedAt")
                company = ""
                if item.get("company") != None:
                    company = item.get("company")
                node.company = company
                
            for item in followingList:
                # print(item)
                node = resp.data.user.following.nodes.add()
                # node = following.nodes.add()
                node.login = item.get("login")
                node.isSiteAdmin = item.get("isSiteAdmin")
                email = ""
                if item.get("email") != None:
                    email = item.get("email")
                node.email = email
                name = ""
                if item.get("name") != None:
                    name = item.get("name")
                node.name = name
                node.updatedAt = item.get("updatedAt")
                company = ""
                if item.get("company") != None:
                    company = item.get("company")
                node.company = company

            print(resp)
                
            followersPageInfo = data.get("data").get("user").get("followers").get("pageInfo")
            followingPageInfo = data.get("data").get("user").get("following").get("pageInfo")
            
            # haveNextFollowersPage = data.get("data").get("user").get("followers").get("pageInfo").get("hasNextPage")
            # haveNextFollowingPage = data.get("data").get("user").get("following").get("pageInfo").get("hasNextPage")
            # currentFollowerEndCursor = data.get("data").get("user").get("followers").get("pageInfo").get("endCursor")
            # currentFollowingEndCursor = data.get("data").get("user").get("following").get("pageInfo").get("endCursor")
            # print("---------------------:{0},{1},{2},{3},{4}".format(currentUser,haveNextFollowersPage,currentFollowerEndCursor,haveNextFollowingPage,currentFollowingEndCursor))
            # print("haveNextFollowersPage:{0}".format(haveNextFollowersPage))
            # print("haveNextFollowingPage:{0}".format(haveNextFollowingPage))

    except Exception as e:
        # print("done op:{0},data:{1}".format(op,json.dumps(data)))
        traceback.print_exc()
        # print(e)

class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst=Dict()
    for k,v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst

if __name__ == '__main__':
    beginReq("liangyuanpeng",True,"22987b33dcb0e2a86b7c7557ef4f320edff9f44f",'','')
    serve()