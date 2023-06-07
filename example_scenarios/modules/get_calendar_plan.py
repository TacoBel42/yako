from typing import Any
import requests
from aiogram.types import Message
from lxml import etree

cookies = {
'PHPSESSID': '',
'hotlog': '1',
'SL_G_WPT_TO': 'ru',
'SL_GWPT_Show_Hide_tmp': '1',
'SL_wptGlobTipTmp': '1',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'PHPSESSID=; hotlog=1; SL_G_WPT_TO=ru; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1',
    'Referer': 'https://vega.fcyb.mirea.ru/sitemap.php',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'id': '194',
}


async def call(state: dict[str, Any], message: Message):
    response = requests.get('https://vega.fcyb.mirea.ru/disc/disc.php', params=params, cookies=cookies, headers=headers)
    htmlparser = etree.HTMLParser()
    tree = etree.fromstring(response.text, htmlparser)
    values = tree.xpath('//tr/td//*[contains(concat(" ",normalize-space(@class)," ")," table-cell ")]/text()')
    result = ''
    for i, v in enumerate(values):
        if i % 4 == 0:
            result += '\n'
        result += v + ' '
    state['calendar'] = result
    return state
    
def init():
    pass