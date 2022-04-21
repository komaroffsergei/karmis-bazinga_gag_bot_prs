import json
import locale
import os
import pathlib
import random
import re
from asyncio import sleep
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

from mega import Mega
from pyquery import PyQuery as pq

story_min = 0
short_story_ls = story_min
short_story_le = story_min + 250

middle_story_ls = short_story_le
middle_story_le = short_story_le + 900

long_story_ls = middle_story_ls
long_story_le = -1
cwd = os.getcwd()
parser_path = cwd + "\\storage\\text\\bash_org_ru"
i_path = parser_path + "\\info.json"
c_path = parser_path + "\\info.json"
parser_path_lib = pathlib.Path(parser_path)

structured = False
d = {
    'января': 'январь',
    'февраля': 'февраль',
    'марта': 'март',
    'апреля': 'апрель',
    'мая': 'май',
    'июня': 'июнь',
    'июля': 'июль',
    'августа': 'август',
    'сентября': 'сентябрь',
    'октября': 'октябрь',
    'ноября': 'ноябрь',
    'декабря': 'декабрь',
}


def store_mega(i, d, q_ent, l, a):
    # ld = 's'
    # if l <= short_story_le:
    #     ld = 's'
    # elif l > short_story_le and l <= middle_story_le:
    #     ld = 'm'
    # elif l > middle_story_le:
    #     ld = 'l'
    p = cwd + '\\storage\\text\\bash_org_ru\\' + str(l) + '-' + str(i) + '.json'
    with open(p, 'a+') as outfile:
        json.dump({
            'i': i,
            'd': d.date(),
            'q': q_ent,
            'l': l,
            'a': a
        }, outfile, indent=4, sort_keys=True, default=str)

def selecter(file, goal, rules):
    rng = range(0, 0)
    if goal == 's':
        rng = range(rules['ss'], rules['se'])
    elif goal == 'm':
        rng = range(rules['ms'], rules['me'])
    elif goal == 'b':
        rng = range(rules['bs'], rules['be'])
    name_parts = file.name.split('-')
    try:
        return int(name_parts[0]) in rng
    except ValueError:
        return False


def find_mega(i):
    json_info = read_info_file()
    be = json_info['b']
    bs = int(json_info['b']-(json_info['b']*0.4))
    se = int(json_info['s'] + (json_info['b']*0.2))
    ss = json_info['s']
    me = bs-1
    ms = se+1


    # [0-9]+\-[0-9]+\.json // eq
    # [0-9]+\.json // find
    #
    # if f.match('[0-9]+\-[0-9]+\.json')
    # filter(re.compile(pattern).match, strings)
    files = [f for f in parser_path_lib.iterdir() if selecter(f, 'm', {
        'bs': bs,
        'be': be,
        'ms': ms,
        'me': me,
        'ss': ss,
        'se': se

    }) is True]
    file = random.sample(files, 1)[0]
    text = file.read_text()
    json_quote = json.loads(text)

    # json.load(json_file)

    # with open(i_path, mode='r', encoding='utf-8') as json_file:
    #     try:
    #         res = json.load(json_file)
    #     except JSONDecodeError:
    #         json_info = {
    #             's': 0,
    #             'b': 0,
    #             'cache_page': 1
    #         }
    #         json.dump(json_info, json_file)
    #         res = json_info
    #     finally:
    #         return res
    print(json_quote['q'])
    # p = cwd + '\\storage\\\text\\bash_org_ru\\+' + i +'+\.json'
    # d = glob.glob(p)
    # print(d)
    return True


def update_info_file(s, b, cache_page):
    json_info = read_info_file()

    _s = s if s != 0 else json_info['s']
    _b = b if b != 0 else json_info['b']
    _cache_page = cache_page if cache_page != 0 else json_info['cache_page']
    json_info = {
        's': _s,
        'b': _b,
        'cache_page': _cache_page
    }
    with open(i_path, 'w') as outfile:
        json.dump(json_info, outfile)

    return json_info


def read_info_file():
    mode = 'r'
    res = None
    if os.path.isfile(i_path) is False:
        mode = 'w+'
    with open(i_path, mode=mode, encoding='utf-8') as json_file:
        try:
            res = json.load(json_file)
        except JSONDecodeError:
            json_info = {
                's': 0,
                'b': 0,
                'cache_page': 1
            }
            json.dump(json_info, json_file)
            res = json_info
        finally:
            return res


def parse():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    if os.path.isdir(parser_path) is False:
        os.makedirs(parser_path, 0o666)
    json_info = read_info_file()
    # db
    # structured = create_tables()
    # if structured is not True:
    #     print('Cant create structure')
    #     return False

    page = pq(url='http://bashorg.org/page/1', parser='html')
    pages = page('#page .navigation a')
    count = pages.length
    max_page = int(pages[count - 2].text)
    cache_page = json_info['cache_page']
    for page_num in range(cache_page, max_page):
        update_info_file(0, 0, page_num)
        print('------------- page N: ' + str(page_num) + ' ----------------')

        page = pq(url='http://bashorg.org/page/' + str(page_num), parser='html')
        quotes = page('#page .quote').length
        for q_num in range(quotes):
            sleep(0.5)
            q_dirty = page.find('.q').eq(q_num)
            if q_dirty and q_dirty.text:
                q_dirty_text = q_dirty.text()
                q_text = q_dirty_text.split('bash.org.ru')[1].split('\n+')[0]
                i = int(q_dirty_text.split(':')[0].split(' | ')[0].split('#')[1])  # id
                found = find_mega(i)
                if found is not True:
                    q_ent = re.sub('<.*?>', '', q_text.split('\n+')[0]).strip()
                    d = get_date(q_dirty_text.split('\n')[0].split('|')[1].strip())
                    l = len(q_text.replace(" ", ""))
                    # store_mega(i, d, q_ent, l, '1')
                    json_info = read_info_file()
                    if json_info['s'] == 0 or json_info['s'] > l:
                        update_info_file(l, 0, page_num)
                    if json_info['b'] == 0 or json_info['b'] < l:
                        update_info_file(0, l, page_num)
                    # store(i, d.date(), q_ent, l, '1')
                    print(">>>>Quote N:" + str(i) + " from " + str(d.date()) + " added")
                else:
                    print(">>>>Quote N:" + str(i) + " skipped")


def get_date(dt):
    for k, v in d.items():
        dt = dt.replace(k, v)
    date_obj = datetime.strptime(dt, '%d %B %Y')

    return date_obj


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mega = Mega()
    m = mega.login(os.environ["MEGA_EMAIL"], os.environ["MEGA_PASSWORD"])
    details = m.get_user()
    parse()
