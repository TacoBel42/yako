import os
from typing import Any
import requests
from aiogram.types import Message
from lxml import etree

cookies = {
'PHPSESSID': os.getenv("VEGA_SESSION"),
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


def get_calendar(tree, state: dict[str, Any]):
    values = tree.xpath('//tr/td//*[contains(concat(" ",normalize-space(@class)," ")," table-cell ")]/text()')
    result = ''
    for i, v in enumerate(values):
        if i % 4 == 0:
            result += '\n'
        result += v + ' '
    state['calendar'] = result
    return state

def get_bac_leaders(tree, state: dict[str, Any]):
    container = 'normalize-space(//div[count(preceding-sibling::*)=8]/div[contains(concat(" ",normalize-space(@class)," ")," tinymce ")]/table/tbody/tr[{}]/td[{}])'
    rows = len(tree.xpath('//div[count(preceding-sibling::*)=8]/div[contains(concat(" ",normalize-space(@class)," ")," tinymce ")]/table/tbody/tr'))
    result = {}
    for i in range(1, rows+1):
        result[tree.xpath(container.format(i, 1))] = [tree.xpath(container.format(i, 2)), tree.xpath(container.format(i, 3))]
    state['bac_leaders'] = result
    return state

def get_mag_leaders(tree, state: dict[str, Any]):
    values = tree.xpath('//div[count(preceding-sibling::*)=9]/div[contains(concat(" ",normalize-space(@class)," ")," tinymce ")]/table/tbody/tr/td/p/span/text()')
    values = list(filter(lambda x: x!= '\xa0', values))
    result = {}
    for i in range(0, len(values), 3):
        if i >= len(values):
            break
        result[values[i]] = [values[i+1], values[i+2]]
    state['mag_leaders'] = result
    return state

def get_leader_contacts(tree, state: dict[str, Any]):
    container = 'normalize-space(//div[count(preceding-sibling::*)=10]/div[contains(concat(" ",normalize-space(@class)," ")," tinymce ")]/table/tbody/tr[count(preceding-sibling::*)={}]/td[count(preceding-sibling::*)={}])'
    rows = len(tree.xpath('//div[count(preceding-sibling::*)=10]/div[contains(concat(" ",normalize-space(@class)," ")," tinymce ")]/table/tbody/tr'))
    result = []
    for i in range(0, rows,):
        result.append(tree.xpath(container.format(i, 0)) + ' - ' + ' '.join([tree.xpath(container.format(i, 1)), tree.xpath(container.format(i, 2))]))
    state['cont_leaders'] = result
    return state

async def call(state: dict[str, Any], message: Message):
    response = requests.get('https://vega.fcyb.mirea.ru/disc/disc.php', params=params, cookies=cookies, headers=headers)
    htmlparser = etree.HTMLParser()
    tree = etree.fromstring(response.text, htmlparser)
    state = get_calendar(tree, state)
    state = get_bac_leaders(tree, state)
    state = get_mag_leaders(tree, state)
    state = get_leader_contacts(tree, state)
    return state
    
def init():
    pass