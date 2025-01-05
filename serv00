"""
需添加环境变量 serv00_ACCOUNTS ，值如下

[
    {
        "hostname": "host1.example.com",
        "port": 22,
        "username": "user1",
        "password": "password1"
    },
    {
        "hostname": "host2.example.com",
        "port": 22,
        "username": "user2",
        "password": "password2"
    }
]

cron: 0 15 15 * *
const $ = new Env("serv00");
"""

import paramiko
import os
import json


# 从环境变量加载SSH账号信息
def load_ssh_accounts():
    ssh_accounts = os.environ.get("serv00_ACCOUNTS")
    if ssh_accounts:
        return json.loads(ssh_accounts)
    else:
        raise ValueError("未找到环境变量 SSH_ACCOUNTS")

def ssh_login(hostname, port, username, password, command):
    try:
        # 创建SSH客户端
        client = paramiko.SSHClient()
        
        # 自动添加主机密钥（第一次连接时）
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接到SSH服务器
        client.connect(hostname, port=port, username=username, password=password)
        
        print(f"成功连接到 {username}")
        
        # 执行命令
        stdin, stdout, stderr = client.exec_command(command)
        
        # 输出命令执行结果
        print(f"命令输出 ({command}):")
        print(stdout.read().decode())
        
        # 关闭连接
        client.close()
        
    except Exception as e:
        print(f"连接到 {hostname} {username} 失败: {e}")

if __name__ == "__main__":
    # 加载SSH账号信息
    ssh_accounts = load_ssh_accounts()
    
    # 要执行的命令
    command = "ls -l"
    
    # 遍历所有SSH账号并执行命令
    for account in ssh_accounts:
        print(f"正在连接 {account['hostname']}...")
        ssh_login(account["hostname"], account["port"], account["username"], account["password"], command)
        print("-" * 40)  # 分隔线
