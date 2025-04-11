# 客户端程序
# 导入模块
import asyncio
# 导入自定义id读取函数
from read_id import *


# 后续可按实际情况更改地址及端口
server_host = '127.0.0.1'
server_port = 8888


# 处理服务端连接(以本地连接为例)
async def client(host=server_host, port=server_port):
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
        print(correct_response)

        # 验证通过，进入通信循环
        writer.write('Hello'.encode('utf-8'))
        await writer.drain()
        # 等待服务器回应，与其原样返回发送数据
        data = await reader.read(1000)
        received_data = data.decode('utf-8').strip()
        print(f'接收的数据为:\n{received_data}')
        return received_data  # 返回接收的数据

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


# 运行客户端程序
if __name__ == '__main__':
    asyncio.run(client())
