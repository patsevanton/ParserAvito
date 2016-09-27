#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests
from lxml import html
import urllib.parse
import urllib.request
import smtplib
import io
import time

#urls = ['acer', 'alcatel', 'asus', 'bq', 'dexp', 'explay', 'fly', 'highscreen', 'htc',
#'huawei', 'lenovo', 'lg', 'meizu', 'motorola', 'philips', 'prestigio', 'samsung', 'xiaomi', 'zte', 'drugie_marki']

#urls = ['acer', 'bq', 'dexp']


class Avito(object):
    MAX_SUMM = 8000
    MIN_SUMM = 2500
    RESULT = []

    def isNotEnglish(s):
        try:
            s.decode('ascii')
        except UnicodeDecodeError:
            return True
        else:
            return False

    def parse_avito_run(self, model):
        header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        url = 'https://www.avito.ru/omsk/telefony/' + model + '?bt=1'
        r = requests.get(url, headers=header)
        res = html.fromstring(r.content)
        result = res.xpath(u'//*[contains(text(), "Последняя")]/@href')
        if result:
            print('34\n', result, '\n')
            num = self._get_page_num(result[0])
            print('36\n', num, '\n')
            result = self.get_page_data(num, model)
            print('38\n', result, '\n')
            return result
        else:
            result = self.get_page_data(1, model)
            print('42\n', result, '\n')
            return result

    def get_page_data(self, num, model):
        print('46\n', num)
        header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        url = 'https://www.avito.ru/omsk/telefony/' + model + '?bt=1'
        if num > 1:
            for i in range(1, num):
                print('51\n', i, '\n')
                r = requests.get(url.format(i), headers=header)
                print('53\n', r, '\n')
                self.get_all(r.content)
                time.sleep(20)
            return self.RESULT
        else:
            print('58\n', num, '\n')
            r = requests.get(url.format(num), headers=header)
            print('60\n', r, '\n')
            self.get_all(r.content)
            time.sleep(20)
        return self.RESULT

    def _get_page_num(self, href):
        print('66\n', href, '\n')
        result = urllib.parse.urlparse(href)
        print('68\n', result, '\n')
        result = urllib.parse.parse_qs(result.query)
        print('70\n', result, '\n')
        return int(result['p'][0])

    def get_all(self, data):
        data = self._get_desc(data)
        #print('63\n', data, '\n')
        for key, i in enumerate(data):
            #print('65\n', key, i, '\n')
            href = i.xpath('//h3[@class="title item-description-title"]/a/@href')[key]
            print('79\n', href, '\n')
            title = i.xpath('//h3[@class="title item-description-title"]/a/@title')[key]
            title = title.replace(" в Омске", "")
            title = title.replace("на iPhone 5.5s", "")
            title = title.replace("на iPhone 5s", "")
            title = title.replace("на iPhone 4s", "")
            title = title.replace("на iPhone 4-4S", "")
            print(title)
            #if self.isNotEnglish(title):
            #    continue
            if 'запчасти' in title:
                continue
            if 'на разбор' in title:
                continue
            print('81\n', title, '\n')
            #address = i.xpath('//p[@class="address fader"]/text()')[key]
            summ = i.xpath('//div[@class="about"]/text()[1]')[key]
            print('84\n', summ, '\n')
            summ = summ.strip()
            summ = summ.replace(" руб.", "")
            summ = summ.replace(" ", "")
            if summ:
                summ = int(summ)
                if summ > self.MAX_SUMM:
                    continue
                if summ < self.MIN_SUMM:
                    continue
                if summ == '':
                    continue
                    print('summ = null')

            #else:
                #summ = u'Без цены '
            self.RESULT.append({'title': title,
                                'href': 'https://www.avito.ru' + href,
                                #'address': address,
                                'sum': summ
                                })

    def _get_desc(self, data):
        print('106\n', self.get_from_xpath(data, '//div[@class="description"]'))
        return self.get_from_xpath(data, '//div[@class="description"]')

    def get_from_xpath(self, data, xpath):
        res = html.fromstring(data)
        print('111\n', res.xpath(xpath), '\n')
        return res.xpath(xpath)

if __name__ == '__main__':
    avito = Avito()
    for model in urls:
        time.sleep(20)
        avito.parse_avito_run(model)
        msg = u''
        for res in avito.RESULT:
            for k, i in res.items():
                msg+=str(res[k]).strip()+","
            msg+='\n'
        #print(msg)
        f = io.open('parsed_data.csv', 'w', encoding='utf8')
        f.write(msg)
        f.close()
