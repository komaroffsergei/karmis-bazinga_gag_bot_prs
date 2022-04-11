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


def update_cache_file(page_num):
    cache_file = open("pagecache.txt", "a+")
    cache_file.truncate(0)
    cache_file.seek(0)
    cache_file.close()

    cache_file = open("pagecache.txt", "a+")
    cache_file.write(str(page_num))
    cache_file.close()


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
    cache_file = open("./pagecache.txt", "r")
    stored_page = cache_file.read()
    cache_file.close()
    if not stored_page:
        from_page = 0
    else:
        from_page = int(stored_page)

    for page_num in range(from_page, max_page):
        update_cache_file(page_num)
        print('------------- page N: ' + str(page_num) + ' ----------------')

        page = pq(url='http://bashorg.org/page/' + str(page_num), parser='html')
        # sleep(0.5)
        quotes = page('#page .quote').length
        for q_num in range(quotes):
            q_dirty = page.find('.q').eq(q_num)
            if q_dirty and q_dirty.text:
                q_dirty_text = q_dirty.text()
                q_text = q_dirty_text.split('bash.org.ru')[1].split('\n+')[0]
                i = int(q_dirty_text.split(':')[0].split(' | ')[0].split('#')[1])  # id
                found = find(i)
                if found is not True:
                    q_ent = re.sub('<.*?>', '', q_text.split('\n+')[0]).strip()
                    d = get_date(q_dirty_text.split('\n')[0].split('|')[1].strip())
                    l = len(q_text)
                    store(i, d.date(), q_ent, l, '1')
                    print(">>>>Quote N:" + str(i) + " from " + str(d.date()) + " added")
                else:
                    print(">>>>Quote N:" + str(i) + " skipped")

    update_cache_file(0)




def get_date(dt):
    for k, v in d.items():
        dt = dt.replace(k, v)
    date_obj = datetime.strptime(dt, '%d %B %Y')

    return date_obj


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parse()
