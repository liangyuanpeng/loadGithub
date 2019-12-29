import grpc
import loadgithub_pb2
import loadgithub_pb2_grpc

def run():
    # 连接 rpc 服务器
    channel = grpc.insecure_channel('localhost:50051')
    # 调用 rpc 服务
    stub = loadgithub_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(loadgithub_pb2.HelloRequest(name='czl'))
    print("Greeter client received: " + response.message)
    response = stub.SayHelloAgain(loadgithub_pb2.HelloRequest(name='daydaygo'))
    print("Greeter client received: " + response.message)

if __name__ == '__main__':
    run()