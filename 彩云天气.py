"""
https://platform.caiyunapp.com/application/manage 彩云天气后台管理
需添加环境变量 cytqToken
需添加环境变量 cytqLocations ，值如下

[
    {"name": "北京顺义", "lon": "116.547244", "lat": "40.106011"},
    {"name": "河南安阳", "lon": "114.031890", "lat": "36.183402"}
]

cron: 0 8,12,16,18 * * *
const $ = new Env("彩云天气");
"""

import requests
import json
import notify
import os

# 设置全局变量
api_key = os.environ.get("cytqToken")
locations = os.environ.get("cytqLocations")

def get_weather_info(lon, lat, location_name):
    api_url = f"https://api.caiyunapp.com/v2.6/{api_key}/{lon},{lat}/weather?alert=true&realtime&minutely"
    response = requests.get(api_url)
    data = json.loads(response.text)
    weather = data['result']

    if weather['alert']['content']:
        tip = weather['alert']['content'][0]['description']
    else:
        tip = ""

    info = f""" 
    天气现象: {weather['realtime']['skycon']}    
    温度: {weather['realtime']['temperature']}°C     
    体感温度: {weather['realtime']['apparent_temperature']}°C    
    湿度: {weather['realtime']['humidity']}      
    能见度: {weather['realtime']['visibility']}KM    
    紫外线强度: {weather['realtime']['life_index']['ultraviolet']['desc']}   
    空气质量: {weather['realtime']['air_quality']['description']['chn']}     
    总体感觉: {weather['realtime']['life_index']['comfort']['desc']}     
    
    全天:
    温度:{weather['daily']['temperature'][0]['min']} - {weather['daily']['temperature'][0]['max']}°C, 白天温度:{weather['daily']['temperature_08h_20h'][0]['min']} - {weather['daily']['temperature_08h_20h'][0]['max']}°C, 夜间温度:{weather['daily']['temperature_20h_32h'][0]['min']} - {weather['daily']['temperature_20h_32h'][0]['max']}°C    
    紫外线强度{weather['daily']['life_index']['ultraviolet'][0]['desc']},总体感觉{weather['daily']['life_index']['comfort'][0]['desc']}      
    
    预测:{weather['minutely']['description']},{weather['hourly']['description']}    
    {tip}
    """

    print(info)
    notify.send("【{}】- 实时天气".format(location_name), info)

# 为多个地区定义相应的信息
locations = json.loads(locations)

# 遍历地区信息并获取天气
for location in locations:
    get_weather_info(location["lon"], location["lat"], location["name"])
