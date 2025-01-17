"""
添加python依赖    redis

需添加环境变量 upstash_redis ，值如下

{
    "REDIS_HOST": "your_redis_host",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "your_redis_password"
}

cron: 0 15 * * *
const $ = new Env("upstash-redis");
"""

import os
import json
import notify
import redis
from redis.exceptions import ConnectionError

# 从环境变量加载redis账号信息
def load_redis_accounts():
    redis_accounts = os.environ.get("upstash_redis")
    if redis_accounts:
        return json.loads(redis_accounts)
    else:
        raise ValueError("未找到环境变量 upstash_redis")

# 加载配置文件
config = load_redis_accounts()

try:
    # 连接到 Redis
    r = redis.Redis(
        host=config['REDIS_HOST'],
        port=config['REDIS_PORT'],
        password=config['REDIS_PASSWORD'],
        ssl=True,  # 启用 SSL
        ssl_cert_reqs=None,  # 不验证证书
        decode_responses=True  # 自动解码返回的字节数据为字符串
    )

    # 测试连接
    if r.ping():
        print('成功连接到 Redis')
        msg = f"""
Redis 登录成功  🎉
"""
        notify.send("Upstash-Redis", msg)

    # 示例：设置一个键值对
    r.set('name', 'John Doe')
    print("键值对设置成功: name -> John Doe")

    # 示例：获取键值对
    name = r.get('name')
    print(f"获取到的值: {name}")

    # 示例：删除键
    r.delete('name')
    print("键 'name' 已删除")

except ConnectionError as err:
    print(f"Redis 连接错误: {err}")
    msg = f"""
Redis 登录失败  😹
"""
    notify.send("Upstash-Redis", msg)

except Exception as err:
    print(f"发生错误: {err}")
    msg = f"""
Redis 登录失败  😹
"""
    notify.send("Upstash-Redis", msg)

finally:
    # 关闭 Redis 连接
    if 'r' in locals():
        r.close()
        print("Redis 连接已关闭")
