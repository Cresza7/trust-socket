# 测试程序
# 导入模块
import pytest
import asyncio
import os
# 将编写的客户端与服务端程序导入
from server import main as server_main
from client import client


# 返回服务器端口号，在后续测试函数中自动写入
@pytest.fixture
def port():
    return 8888


# 测试1 客户端和服务端使用相同的TRUST ID(结果应为验证通过并通信成功)
@pytest.mark.asyncio
async def test_correct_id(port):
    # 修改环境变量的方式，写入TRUST_ID(都使用1000)
    os.environ['TRUST_ID'] = '1000'  # 不添加该行也行，在程序运行时会查找相应文件中的TRUST ID，下同

    # 启动服务端
    server_task = asyncio.create_task(server_main(port=port))
    await asyncio.sleep(0.5)  # 等待服务端启动

    try:
        # 运行客户端，若匹配成功程序应无异常
        await client(port=port)
        # 验证通信结果
        response = await client(port=port)
        assert response == 'Hello'
    finally:
        # 关闭通信
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    del os.environ['TRUST_ID']  # 清理环境变量


# 测试2 客户端和服务端TRUST ID不匹配(结果应有异常)
@pytest.mark.asyncio
async def test_incorrect_id(port):
    # 服务端环境变量中的TRUST_ID为1001
    os.environ['TRUST_ID'] = '1001'

    # 启动服务端
    server_task = asyncio.create_task(server_main(port=port))
    await asyncio.sleep(0.5)

    try:
        # 修改客户端TRUST_ID为1002
        os.environ['TRUST_ID'] = '1002'
        # 此时调用客户端应抛出异常
        with pytest.raises(ConnectionError, asyncio.IncompleteReadError):
            await client(port=port)
    finally:
        # 同样关闭通信
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    del os.environ['TRUST_ID']
