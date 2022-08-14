from typing import List
import httpx
import traceback
import jinja2
import re
import time
import asyncio
from pathlib import Path
from .data_source import servers,set_damageColor,set_winColor,set_upinfo_color,select_prvalue_and_color
from .publicAPI import get_all_shipList
from nonebot_plugin_htmlrender import html_to_pic
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from httpx import ConnectTimeout
from asyncio.exceptions import TimeoutError
from .utils import match_keywords,get_bot
from threading import Thread

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)
env.globals.update(set_damageColor=set_damageColor,set_winColor=set_winColor,set_upinfo_color=set_upinfo_color,time=time,int=int,abs=abs,enumerate=enumerate)

headers = {
    'Authorization': get_driver().config.api_token
}

all_shipList = asyncio.run(get_all_shipList())

async def send_realTime_message(data):
    try:
        global all_shipList
        if not all_shipList:
            all_shipList = await get_all_shipList()
        bot = get_bot()
        template = env.get_template("wws-realTime.html")
        template_data = await set_realTime_params(data)
        content = await template.render_async(template_data)
        print(content)
        #coroutine = send_message(content)
        #loop = asyncio.new_event_loop()
        #task = loop.create_task(coroutine)
        #loop.run_until_complete(task)
        img = await html_to_pic(content, wait=0, viewport={"width": 1800, "height": 1000})
        #await bot.send_group_msg(group_id=574432871,message=f"[测试功能]雨季刚刚进入了一场战斗\n")
        await bot.send_group_msg(group_id=574432871,message=MessageSegment.image(img))
        #await bot.send_group_msg(group_id=967546463,message=f"[测试功能]雨季刚刚进入了一场战斗\n")
        #await bot.send_group_msg(group_id=639178962,message=f"[测试功能]雨季刚刚进入了一场战斗\n")
    except Exception:
        logger.error(traceback.format_exc())
        return
    
async def set_realTime_params(data):
    try:
        player_count = len(data['infoList'])
        for each_player in data['infoList']:
            each_player['shipImgSmall'] = None
            for each_ship in all_shipList:
                if each_ship['id'] == each_player['shipId']:
                    if each_ship['shipNameCn']:
                        each_player['shipName'] = each_ship['shipNameCn']
                    else:
                        each_player['shipName'] = each_ship['name']
                    each_player['shipImgSmall'] = each_ship['imgSmall']
                    break
            each_player['pvp']['pr_name'],each_player['pvp']['pr_color'] = await select_prvalue_and_color(each_player['pvp']['pr'])
            each_player['ship']['pr_name'],each_player['ship']['pr_color'] = await select_prvalue_and_color(each_player['ship']['pr'])
        data['player_count'] = player_count
        logger.success(data)
        return data
    except Exception:
        logger.error(traceback.format_exc())
        return None
    
async def send_message(content):
    bot = get_bot()
    img = await html_to_pic(content, wait=0, viewport={"width": 1800, "height": 1000})
    await bot.send_group_msg(group_id=574432871,message=MessageSegment.image(img))