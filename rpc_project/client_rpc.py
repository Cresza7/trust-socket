# RPC客户端程序
# 导入模块
import asyncio
import json
import uuid
# 导入自定义id读取函数
from read_id import *


# 后续可按实际情况更改地址及端口
server_host = '127.0.0.1'
server_port = 9999


# 与服务端连接
async def rpc_call(method, params=None, host=server_host, port=server_port):
    # 读取客户端本地Trust ID
    trust_id = get_trust_id(filename='client_trust_id.txt')

    # 发送TRUST ID到服务端进行验证
    try:
        # 建立连接，获得读取及写入对象
        reader, writer = await asyncio.open_connection(host, port)
        # 发送TRUST ID
        writer.write(trust_id.encode('utf-8'))
        await writer.drain()

        # 接受来自服务器的验证响应(以utf-8编码，下同)
        response = await reader.read(1000)
        correct_response = 'TRUST ID验证通过！'  # 验证通过收到的响应
        if response.decode('utf-8') != correct_response:
            raise ConnectionError('ERROR: TRUST ID验证失败！')
        # print(correct_response)

        # 验证通过，进入通信
        # 构造请求数据(函数名、参数列表、请求编号、是否异步调用)
        req_id = str(uuid.uuid4())
        request = {
            'method': method,
            'params': params or [],
            'id': req_id,
            'async': True
        }

        # 发送请求
        writer.write(json.dumps(request).encode('utf-8'))
        await writer.drain()

        # 等待服务器回应
        data = await reader.read(10000)
        # 异常报错提醒
        response = json.loads(data.decode('utf-8'))
        if 'ERROR' in response:
            print(response)
            raise Exception(response['ERROR'])

        # print(f'结果为:\n{response['result']}')
        return response['result']

    # 异常报错
    except (asyncio.IncompleteReadError, ConnectionRefusedError) as e:
        print(f'连接异常: {e}')
        raise ConnectionError('连接异常') from e  # 抛出异常供测试捕获、下同
    except Exception as e:
        print(f'错误: {e}')
        raise

    # 关闭连接、结束通信
    finally:
        writer.close()
        await writer.wait_closed()


# 同步调用封装函数
def rpc_call_sync(method, params=None, host=server_host, port=server_port):
    return asyncio.run(rpc_call(method, params, host, port))


# 异步调用
async def main():
    result = await rpc_call('add', [3, 5])
    print('异步RPC返回结果:', result)

# 同步调用
if __name__ == '__main__':
    print('同步RPC返回结果:', rpc_call_sync('echo', ['hello']))
    print('-' * 50)
    asyncio.run(main())
