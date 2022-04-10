import locale
import re
from datetime import datetime
from time import sleep
from pyquery import PyQuery as pq

from db import create_tables, find, store

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


def parse():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    # db
    structured = create_tables()
    if structured is not True:
        print('Cant create structure')
        return False

    page = pq(url='http://bashorg.org/page/1', parser='html')
    pages = page('#page .navigation a')
    count = pages.length

    max_page = int(pages[count - 2].text)
    for page_num in range(568, max_page):

        print('------------- page N: ' + str(page_num) + ' ----------------')

        page = pq(url='http://bashorg.org/page/' + str(page_num), parser='html')
        sleep(1)
        quotes = page('#page .quote').length
        for q_num in range(quotes):
            q_dirty = page.find('.q').eq(q_num)
            if q_dirty and q_dirty.text:
                q_text = q_dirty.text()
                i = int(q_text.split(':')[0].split(' | ')[0].split('#')[1])  # id
                found = find(i)
                if found is not True:
                    q_ent = re.sub('<.*?>', '', q_text.split('\n+')[0]).strip()
                    d = get_date(q_text.split('\n')[0].split('|')[1].strip())
                    l = len(q_text)
                    store(i, d.date(), q_ent, l, '1')
                    sleep(.2)
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
    parse()
