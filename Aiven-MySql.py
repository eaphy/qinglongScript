"""
添加python依赖    mysql-connector-python

需添加环境变量 aiven_Mysql ，值如下

{
    "DB_USER": "",
    "DB_PASSWORD": "",
    "DB_HOST": "",
    "DB_PORT": 3306,
    "DB_NAME": "",
    "LOGIN_USER": "",
    "LOGIN_PASSWORD": ""
}

cron: 0 15 * * *
const $ = new Env("aiven-mysql");
"""

import mysql.connector
import os
import json
import notify
import requests


# 从环境变量加载SSH账号信息
def load_mysql_accounts():
    mysql_accounts = os.environ.get("aiven_Mysql")
    if mysql_accounts:
        return json.loads(mysql_accounts)
    else:
        raise ValueError("未找到环境变量 aiven_Mysql")

# 加载配置文件
config = load_mysql_accounts()

# 登录
def aiven_console_login():
    url = "https://console.aiven.io/v1/userauth"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": config['LOGIN_USER'],
        "password": config['LOGIN_PASSWORD'],
        "tenant": "aiven"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        print("Aiven 控制台登录成功")
        return response.json()  # 返回响应的JSON数据
    except requests.exceptions.RequestException as err:
        print(f"Aiven 控制台登录失败: {err}")
        return None

login_response = aiven_console_login()
if login_response:
    print("登录响应:", login_response)
    msg = f"""
MySQL 登录成功  🎉
"""
    notify.send("Aiven-Mysql", msg)


try:
    # 连接到 MySQL 数据库
    conn = mysql.connector.connect(
        user=config['DB_USER'],
        password=config['DB_PASSWORD'],
        host=config['DB_HOST'],
        database=config['DB_NAME'],
        port=config['DB_PORT'],
        raise_on_warnings=True
    )

    if conn.is_connected():
        print('成功连接到 MySQL 数据库')
        msg = f"""
MySQL 连接数据库成功  🎉
"""
        notify.send("Aiven-Mysql", msg)

        # 创建游标对象
        cursor = conn.cursor()

        # 执行 SQL 查询
        cursor.execute("SELECT VERSION()")

        # 获取查询结果
        db_version = cursor.fetchone()
        print(f"数据库版本: {db_version[0]}")

        # 示例：查询数据
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        print("员工数据:")
        for row in rows:
            print(row)

except mysql.connector.Error as err:
    print(f"错误: {err}")
    msg = f"""
MySQL登录失败  😹
"""
    notify.send("Aiven-Mysql", msg)

finally:
    # 关闭游标和连接
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("MySQL 连接已关闭")
