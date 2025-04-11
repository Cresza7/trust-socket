# 服务端程序
# 导入模块
import asyncio
# 导入自定义id读取函数
from read_id import *


# 处理客户端连接
async def handle_client(reader, writer, server_id):
    # 对客户端连接进行验证
    try:
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

        # 进入通讯循环(示例)
        while True:
            data = await reader.read(1000)
            # 有无数据验证
            if not data:
                writer.write('未发送数据，请检查！'.encode('utf-8'))
                await writer.drain()
                break
            # 原样返回客户端数据(示例)
            writer.write(data)
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
server_port = 8888


# 主函数启动服务器(以本地地址为例，方便测试)
async def main(host=server_host, port=server_port):
    # 读取本地TRUST ID以便验证
    server_id = get_trust_id(filename='server_trust_id.txt')
    # 启动TCP服务器并监听、传递正确TRUST ID
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, server_id), host, port)

    # 管理服务器生命周期
    async with server:
        print(f'服务器启动，TRUST ID为：{server_id}')
        # 永久运行服务器，接受客户端连接
        await server.serve_forever()


# 运行服务器端程序
if __name__ == '__main__':
    asyncio.run(main())
