# RPC服务端程序
# 导入模块
import asyncio
import json
# 导入自定义id读取函数
from read_id import *

# 注册远程可被调用的函数(以简单的求和及echo函数为例)
functions = {
    # 函数名: 可执行函数
    'add': lambda x, y: x + y,
    'echo': lambda msg: msg
}


async def handle_rpc(reader, writer, server_id):
    try:
        # 先对客户端连接进行验证
        # 读取客户端TRUST ID(以短ID为例)
        data = await reader.read(100)
        # 验证是否有数据
        if not data:
            # 无数据报错
            raise ValueError('ERROR：接收数据为空！')

        # 有数据情况下验证TRUST ID是否一致(以utf-8编码，下同)
        client_id = data.decode('utf-8').strip()
        if client_id != server_id:
            # 向客户端发送通知
            writer.write('ERROR: TRUST ID验证失败！'.encode('utf-8'))
            await writer.drain()
            # 同时本地运行时报错
            raise ValueError('ERROR：TRUST ID验证失败！')

        # 验证通过，发送成功通知
        writer.write('TRUST ID验证通过！'.encode('utf-8'))
        await writer.drain()

        # 读取客户端请求
        data = await reader.read(10000)
        request = json.loads(data.decode('utf-8'))  # 接收到的JSON字符串解码

        # 提取字段(函数名、参数列表、请求编号)
        method = request.get('method')
        params = request.get('params', [])
        req_id = request.get('id')

        # 若函数请求的函数不存在，返回错误信息
        if method not in functions:
            response = {'ERROR': f'{method}不存在', 'id': req_id}
        else:
            # 函数存在则调用。并传入参数
            try:
                result = functions[method](*params)
                response = {'result': result, 'id': req_id}
            # 调用失败则捕获异常并返回错误消息
            except Exception as e:
                response = {'ERROR': e, 'id': req_id}

        # 返回JSON字符串响应
        writer.write(json.dumps(response).encode())
        await writer.drain()

    # 异常报错
    except (asyncio.IncompleteReadError, ConnectionResetError) as e:
        print(f'客户端异常断开: {e}')
        raise ConnectionError('连接异常') from e
    except Exception as e:
        print(f'服务端错误: {e}')
        raise

    # 关闭连接，结束通信
    finally:
        writer.close()
        await writer.wait_closed()


# 后续可按实际情况更改地址及端口
server_host = '127.0.0.1'
server_port = 9999


# 主函数启动服务器(以本地地址为例，方便测试)
async def main(host=server_host, port=server_port):
    # 读取本地TRUST ID以便验证
    server_id = get_trust_id(filename='server_trust_id.txt')
    server = await asyncio.start_server(lambda r, w: handle_rpc(r, w, server_id), host, port)
    async with server:
        print(f'RPC服务器启动，TRUST ID为：{server_id}')
        # 永久运行服务器，接受客户端连接
        await server.serve_forever()


async def start_server(host=server_host, port=server_port):
    server = await asyncio.start_server(lambda r, w: handle_rpc(r, w, server_id), host, port)
    print(f'Started RPC server at {host}:{port}')
    return server


# 运行RPC服务器端程序
if __name__ == '__main__':
    asyncio.run(main())
