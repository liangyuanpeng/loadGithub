# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import loadgithub_pb2 as loadgithub__pb2


class GreeterStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SayHello = channel.unary_unary(
        '/service.Greeter/SayHello',
        request_serializer=loadgithub__pb2.HelloRequest.SerializeToString,
        response_deserializer=loadgithub__pb2.HelloReply.FromString,
        )
    self.SayHelloAgain = channel.unary_unary(
        '/service.Greeter/SayHelloAgain',
        request_serializer=loadgithub__pb2.HelloRequest.SerializeToString,
        response_deserializer=loadgithub__pb2.HelloReply.FromString,
        )


class GreeterServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def SayHello(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SayHelloAgain(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SayHello': grpc.unary_unary_rpc_method_handler(
          servicer.SayHello,
          request_deserializer=loadgithub__pb2.HelloRequest.FromString,
          response_serializer=loadgithub__pb2.HelloReply.SerializeToString,
      ),
      'SayHelloAgain': grpc.unary_unary_rpc_method_handler(
          servicer.SayHelloAgain,
          request_deserializer=loadgithub__pb2.HelloRequest.FromString,
          response_serializer=loadgithub__pb2.HelloReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'service.Greeter', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class GithubLoaderStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.QueryFollow = channel.unary_unary(
        '/service.GithubLoader/QueryFollow',
        request_serializer=loadgithub__pb2.QueryFollowRequest.SerializeToString,
        response_deserializer=loadgithub__pb2.QueryFollowResp.FromString,
        )


class GithubLoaderServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def QueryFollow(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GithubLoaderServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'QueryFollow': grpc.unary_unary_rpc_method_handler(
          servicer.QueryFollow,
          request_deserializer=loadgithub__pb2.QueryFollowRequest.FromString,
          response_serializer=loadgithub__pb2.QueryFollowResp.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'service.GithubLoader', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))