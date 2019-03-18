import copy
import re
import time

import requests
from PIL import Image
from bs4 import BeautifulSoup


class Spider:

    def __init__(self, url):
        self.__uid = ''
        self.__real_base_url = ''
        self.__name = ''
        self.__base_url = url
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        self.__base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '',
            'ddl_kcgs': '',
            'ddl_xqbs': '2',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }

    def __set_real_url(self):
        request = requests.get(self.__base_url, headers=self.__headers)
        real_url = request.url
        self.__real_base_url = real_url[:len(real_url) - len('default2.aspx')]
        return request

    def get_cookie(self):
        request = self.__set_real_url()
        print(request.cookies.items())

    def __get_code(self):
        request = requests.get(self.__real_base_url + 'CheckCode.aspx', headers=self.__headers)
        with open('code.jpg', 'wb') as f:
            f.write(request.content)
        im = Image.open('code.jpg')
        im.show()
        print('Write the code below')
        code = input()
        return code

    def __get_login_data(self, uid, password):
        self.__uid = uid
        request = self.__set_real_url()
        soup = BeautifulSoup(request.text)
        form_tag = soup.find('input')
        __VIEWSTATE = form_tag['value']
        code = self.__get_code()

        return {
            '__VIEWSTATE': __VIEWSTATE,
            'txtSecretCode': code,
            'txtUserName': uid,
            'TextBox2': password,
            'RadioButtonList1': '学生'.encode('gb2312'),
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': '',
        }

    def login(self, uid, password):
        while True:
            data = self.__get_login_data(uid, password)
            request = requests.get(self.__real_base_url + 'default2.aspx', headers=self.__headers, data=data)
            soup = BeautifulSoup(request.text)
            try:
                name_tag = soup.find(id='xhxm')
                self.__name = name_tag.string[:len(name_tag.string) - 2]
                print('Welcome', self.__name)
            except:
                print('Error occur, try login again')
                time.sleep(0.5)
                continue
            finally:
                return True

    def __enter_lessons_first(self):
        data = {
            'xh': self.__uid,
            'xm': self.__name.encode('gb2312'),
            'gnmkdm': 'N121203'
        }
        self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
        request = requests.get(self.__real_base_url + 'xf_xsqxxxk.aspx', params=data, headers=self.__headers)
        self.__headers['Referer'] = request.url
        soup = BeautifulSoup(request.url)
        self.__set__VIEWSTATE(soup)

    def __set__VIEWSTATE(self, soup):
        __VIEWSTATE_tag = soup.find('input', attrs={'name': '__VIEWSTATE'})
        self.__base_data['__VIEWSTATE'] = __VIEWSTATE_tag['value']

    def __search_lessons(self, lesson_name=''):
        self.__base_data['TextBox1'] = lesson_name.encode('gb2312')
        request = requests.post(self.__headers['Referer'], data=self.__base_data, headers=self.__headers)
        soup = BeautifulSoup(request.text)
        self.__set__VIEWSTATE(soup)
        return self.__get_lessons(soup)

    def __get_lessons(self, soup):
        lesson_list = []
        lessons_tag = soup.find('table', id='kcmcGrid')
        lesson_tag_list = lessons_tag.find_all('tr')[1:]

        for lesson_tag in lesson_tag_list:
            td_list = lesson_tag.find_all('td')
            code = td_list[0].input['name']
            name = td_list[1].string
            teacher_name = td_list[3].string
            Time = td_list[4]['title']
            number = td_list[10].string
            lesson = self.Lesson(name, code, teacher_name, Time, number)
            lesson_list.append(lesson)

        return lesson_list

    def __select_lesson(self, lesson_list):
        data = copy.deepcopy(self.__base_data)
        data['Button1'] = '  提交  '.encode('gb2312')
        for lesson in lesson_list:
            code = lesson.code
            data[code] = 'on'

        request = requests.post(self.__headers['Referer'], data=data, headers=self.__headers)
        soup = BeautifulSoup(request.text)
        self.__set__VIEWSTATE(soup)
        error_tag = soup.html.head.script
        if not error_tag is None:
            error_tag_text = error_tag.string
            r = "alert\('(.+?)'\);"
            for s in re.findall(r, error_tag_text):
                print(s)

        print('已选课程:')
        selected_lessons_pre_tag = soup.find('legend', text='已选课程')
        selected_lessons_tag = selected_lessons_pre_tag.next_sibling
        tr_list = selected_lessons_tag.find_all('tr')[1:]
        for tr in tr_list:
            td = tr.find('td')
            print(td.string)
