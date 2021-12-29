import re
from datetime import datetime, date, timedelta
import unittest
from time import strptime


class DateNormalizer:
    long_long_ago = '2000-01-01'

    def __init__(self,
                 date_string,
                 current_date,
                 date_format):

        self.rus_month_dict = {
            'янв': 'jan',
            'фев': 'feb',
            'мар': 'mar',
            'апр': 'apr',
            'май': 'may',
            'июн': 'jun',
            'июл': 'jul',
            'авг': 'aug',
            'сен': 'sep',
            'окт': 'oct',
            'ноя': 'nov',
            'дек': 'dec'
        }
        self.current_date = current_date
        self.date_string = self.clean_str(date_string)
        self.date_format = date_format
        self.re_search_list = self.make_re_search_list()

    @staticmethod
    def clean_str(date_string):
        return ' '.join(i.strip() for i in date_string.split() if i).lower()

    def date_from_days_ago(self, day_ago_number):

        return (self.current_date - timedelta(days=day_ago_number))

    def date_from_days_ago_re(self, re_days_ago_compiled):
        days_re = re.search(re_days_ago_compiled, self.date_string)

        return self.date_from_days_ago(int(days_re.group(1)))

    def delimited_date_re(self, compiled_re):
        _date = re.search(compiled_re, self.date_string).groupdict()

        return self.dict_to_date(_date)

    def long_long_ago_re(self, arg):
        return self.date_str_to_date_obj(self.long_long_ago, '%Y-%m-%d')

    @staticmethod
    def date_to_string(date_object, date_format_str):
        try:
            _date = date_object.strftime(date_format_str)
        except AttributeError as _err:
            # sys.stdout.write('Error: %s\n' % _err)
            return None

        return _date

    def check_year(self, date_dict):
        if isinstance(date_dict.get('month'), str) and date_dict.get('month').isdigit():
            _month = int(date_dict['month'])
        else:
            _month = strptime(date_dict['month'], '%b').tm_mon

        if _month > self.current_date.month or (_month >= self.current_date.month and
                int(date_dict['day']) > self.current_date.day):
            _year = self.current_date.year - 1
        else:
            _year = '%d' % self.current_date.year

        return _year

    def date_from_human_format_re(self, re_date_compiled):
        date_re = re.search(re_date_compiled, self.date_string)

        date_dict = date_re.groupdict()
        is_cyrillic = lambda x: bool(re.search('[а-яА-Я]', x))
        month_string = date_dict.get('month').lower()[:3]

        if is_cyrillic(month_string):
            month_string = 'май' if re.match(r'мая', month_string) else month_string
            month_string = self.rus_month_dict.get(month_string)
            if not month_string:
                return

        date_dict['month'] = month_string

        try:
            current_date = self.dict_to_date(date_dict)
        except ValueError as _err:
            return

        return current_date

    def date_str_to_date_obj(self, date_str, date_format_from):
        try:
            _date = datetime.strptime(date_str, date_format_from).date()
        except:
            pass
        else:
            return _date

    def dict_to_date(self, date_dict):

        if not date_dict.get('year'):
            date_dict['year'] = self.check_year(date_dict)

        _year_format = '%Y' if len(str(date_dict['year'])) == 4 else '%y'
        _month_format = '%b' if re.search('[a-z]', date_dict['month']) else '%m'

        if date_dict.get('month') and len(date_dict['month']) == 1:
            date_dict['month'] = '0%s' % date_dict['month']

        if date_dict.get('day') and len(date_dict['day']) == 1:
            date_dict['day'] = '0%s' % date_dict['day']

        if not all(date_dict.values()):
            return

        try:
            date_obj = datetime.strptime(
                '{year}{month}{day}'.format(**date_dict),
                '{}{}%d'.format(_year_format, _month_format)
            ).date()
        except Exception as _err:
            return

        return date_obj

    def make_re_search_list(self):
        re_today = re.compile(r'сегодня|только\sчто|несколько' \
                   '|\d{1,3}\s(мин(ут|уты|уту|\.)?|час(ов|а|\.)?|сек(унд|унды|\.)?)\sназад|^[0-9]{2}[:][0-9]{2}$')

        re_yesterday = re.compile(r'вчера')
        re_before_yesterday = re.compile(r'позавчера')
        re_some_days_ago = re.compile(r'(\d{1,2})\s+(?:дня|день|дней)\s+назад')
        re_long_long_ago = re.compile(r'(более\s+)?\d{1,2}(-х)?\s+(месяц(а|ев)|лет|год|года|недель)\s+назад|в архиве')

        # dd mmm yyyy
        re_human_format_date = re.compile(
            r'(?P<day>\d{1,2})\.?\s?'
            '(?P<month>[а-яa-z]{3,})\.?\s?'
            '(?P<year>\d{2,4})?(?!:)'
        )

        # dd.mm.yyyy
        re_date_dmy_delimiter = re.compile(
            r'^(?P<day>\d{1,2})[.-]'
            '(?P<month>\d{1,2})[.-]?'
            '(?P<year>\d{2,4})?'
        )
        # yyyy.mm.dd
        re_date_ymd_delimiter = re.compile(
            r'(?P<year>\d{4})[.-]'
            '(?P<month>\d{1,2})[.-]?'
            '(?P<day>\d{1,2})?'
        )

        return  (
            (re_today, self.date_from_days_ago, (0,)),
            (re_before_yesterday, self.date_from_days_ago, (2,)),
            (re_yesterday, self.date_from_days_ago, (1,)),
            (re_some_days_ago, self.date_from_days_ago_re, (re_some_days_ago, )),
            (re_long_long_ago, self.long_long_ago_re, (0,)),
            (re_human_format_date, self.date_from_human_format_re, (re_human_format_date, )),
            (re_date_dmy_delimiter, self.delimited_date_re, (re_date_dmy_delimiter, )),
            (re_date_ymd_delimiter, self.delimited_date_re, (re_date_ymd_delimiter, )),
        )

    def re_search(self):
        for _re_compiled, action, args in self.re_search_list:
            if re.search(_re_compiled, self.date_string) and all((action, args)):
                _result = action(*args)
                if not _result:
                    continue

                #print("{} = {} = {}".format(self.date_string, _re_compiled, _result))
                return _result
        else:
            #print("{} = error".format(self.date_string))
            return None

    def get_valid_date(self):
        date_str = self.date_to_string(self.re_search(), self.date_format)

        return date_str

def date_normalize(date_string, current_date=date.today(), date_format='%Y-%m-%d'):
    if date_string is None:
        return
    _date = DateNormalizer(date_string, current_date, date_format)

    return _date.get_valid_date()


class TestDateToAdapter(unittest.TestCase):

    def setUp(self):
        self.current_date = datetime.strptime('2019-02-14', '%Y-%m-%d').date()

        self.cases_tuple = {
            ('20.05.2018', '2018-05-20'),
            ('20-05-2018', '2018-05-20'),
            ('12-11-2019', '2019-11-12'),
            ('12.11.2019', '2019-11-12'),
            ('12.11.2019, 11:23', '2019-11-12'),
            ('2018-01-30', '2018-01-30'),
            ('2018.01.30', '2018-01-30'),
            ('14 ноября 2018', '2018-11-14'),
            ('23 дек 18', '2018-12-23'),
            ('23 фев 18', '2018-02-23'),
            ('23 фев 19', '2019-02-23'),
            ('23фев2019', '2019-02-23'),
            ('6 дней назад', str(self.current_date - timedelta(days=6))),
            ('51 минуту назад', str(self.current_date)),
            ('тест 5 часов назад тест', str(self.current_date)),
            ('тест 3 часа назад тест', str(self.current_date)),
            ('тест сегодня тест', str(self.current_date)),
            ('тест сегодня тест, 9:02', str(self.current_date)),
            ('тест вчера тест', str(self.current_date - timedelta(days=1))),
            ('тест позавчера тест', str(self.current_date - timedelta(days=2))),
            ('12-11', '2018-11-12'),
            ('12.11', '2018-11-12'),
            ('12-02', '2019-02-12'),
            ('15-02', '2018-02-15'),
            ('15.02', '2018-02-15'),
            ('10:04', str(self.current_date)),
            ('15 декабря', '2018-12-15'),
            ('19 февраля', '2018-02-19'),
            ('14 февраля', '2019-02-14'),
            ('25 декабря', '2018-12-25'),
            ('15 декабря 2019', '2019-12-15'),
            ('в архиве', DateNormalizer.long_long_ago),
            ('6 недель назад', DateNormalizer.long_long_ago),
            ('3 месяца назад', DateNormalizer.long_long_ago),
            ('1 год назад', DateNormalizer.long_long_ago),
            ('2 года назад', DateNormalizer.long_long_ago),
            ('5 лет назад', DateNormalizer.long_long_ago),
            ('более 3-х месяцев назад', DateNormalizer.long_long_ago),
        }

    def test_cases(self):
        for test_entry, test_entry_result in self.cases_tuple:
            self.assertEqual(date_normalize(test_entry, self.current_date), test_entry_result)

if __name__ == '__main__':
    unittest.main()
