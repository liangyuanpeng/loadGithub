import logging
import logstash
import sys
import pylru

#logstash host
host = '192.168.2.117'
test_logger = logging.getLogger('logstash-loadgithub')
test_logger.setLevel(logging.INFO)
#创建一个ogHandler
test_logger.addHandler(logstash.LogstashHandler(host, 5044))

test_logger.error('这是一行测试日志')
test_logger.info("测试日志 info")
extra = {
    'test_string': 'python version: ' + repr(sys.version_info),
    'test_boolean': True,
    'test_dict': {'a': 1, 'b': 'c'},
    'test_float': 1.23,
    'test_integer': 123,
    'test_list': [1, 2, '3'],
}
test_logger.info('logstash-loadgithub: test extra fields', extra=extra)

userCache = pylru.lrucache(100000)
userCache['a']=1
map = {
    'a' : "1",
    'b' : "2"
}
userCache.addTailNode(map)
print('a' in userCache)
print(len(userCache.table))
for i in userCache:
    print(i)