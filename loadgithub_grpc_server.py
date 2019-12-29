from concurrent import futures
import time
import grpc
import loadgithub_pb2
import loadgithub_pb2_grpc

# 实现 proto 文件中定义的 GreeterServicer
class Greeter(loadgithub_pb2_grpc.GreeterServicer):
    # 实现 proto 文件中定义的 rpc 调用
    def SayHello(self, request, context):
        return loadgithub_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))

    def SayHelloAgain(self, request, context):
        return loadgithub_pb2.HelloReply(message='hello {msg}'.format(msg = request.name))

class GithubLoader(loadgithub_pb2_grpc.GithubLoaderServicer){
    def QueryFollow(self,request,context):
        return loadgithub_pb2.QueryFollowResp()
}

def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    loadgithub_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60*60*24) # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()