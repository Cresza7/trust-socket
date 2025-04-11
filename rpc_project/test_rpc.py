# RPC测试程序
# 需要先运行RPC服务端程序
# 导入模块
import pytest
import asyncio
import socket
from client_rpc import *
from server_rpc import start_server


# 返回服务器端口号，在后续测试函数中自动写入
@pytest.fixture
def port():
    return 9999


# 测试add方法，验证异步通信调用函数是否正确
@pytest.mark.asyncio
async def test_async_add(port):
    # 运行客户端，若计算正确程序应无异常
    result = await rpc_call('add', [1, 2], port=port)
    # 验证结果
    assert result == 3


# 测试echo方法，验证同步通信调用函数是否正确
def test_sync_echo(port):
    result = rpc_call_sync('echo', ['hello'], port=port)
    assert result == 'hello'


# 调用不存在的方法，测试是否抛出错误
def test_unknown_method(port):
    with pytest.raises(Exception) as exc_info:
        rpc_call_sync('unknown', [], port=port)
    assert 'unknown不存在' in str(exc_info.value)

