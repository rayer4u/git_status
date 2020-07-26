import os
import collections
import sys
import re
from datetime import *
import dateutil.parser
import json
from jinja2 import Template

log_fmt = "git log --since={} --until={}"
calc_endfix = " --pretty='%H %an %aI %s' --numstat"

if __name__ == '__main__':
    print('python3 git_log.py [start_date(本周一) ] [end_date(今天)]')

    if len(sys.argv) > 2:
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
    else:
        end_date = date.today()

    if len(sys.argv) > 1:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        start_date = end_date - timedelta(days=(end_date.weekday()))

    print(log_fmt.format(str(start_date), str(end_date)) + calc_endfix)
    fouput = os.popen(log_fmt.format(
        str(start_date), str(end_date)) + calc_endfix)

    # 工作日，所有有提交记录的日子
    date_list = [str(start_date + timedelta(days=x)) for x in range((end_date - start_date + timedelta(days=1) ).days)]

    data_list = []  #直接的结果
    data = []  # 每次提交
    user = '' # 提交用户
    dimensions = ['hashes', '作者', '提交完整时间', '提交内容', '插入行数', '删除行数', '相对行数',  '提交日期', '提交时间']
    dimensions_day = ['提交', '插入行数', '删除行数', '相对行数',  '提交日期']

    for line in fouput:
        # print(line, end='')
        linel = re.split(r"\s+", line.strip(), maxsplit=3)
        # print(linel)
        if re.match('[0-9a-z]{10,}', linel[0]):  #是否提交hash的检查
            user = linel[1]
            data = linel
            date_time = dateutil.parser.parse(linel[2])
            data.extend([0, 0, 0, str(date_time.date()),  str(date_time.time())])
            date_list.append(str(date_time.date()))
            data_list.append(data)
        elif len(linel) > 2:
            if linel[0] != '-':
                data[4] += int(linel[0])  # 增加行数
            if linel[1] != '-':
                data[5] -= int(linel[1])  # 删除行数
            data[6]= data[4] + data[5]  # 相对行数

    # print(data_dict)

    #  时间队列排序。
    date_list = list(set(date_list))
    date_list.sort()
    # print(date_list)

    data_dict = {}   # 结果，按照user区分的每日统计
    for data in data_list:
        user = data[1]
        if user not in data_dict:
            data_dict[user] = [[[], 0, 0, 0, date] for date in date_list]
        for data_day in data_dict[user]:
            if data_day[4] == data[7]:
                data_day[1] += data[4]  # 增加行数
                data_day[2] += data[5]  # 删除行数
                data_day[3]= data_day[1] + data_day[2]  # 相对行数
                data_day[0].append(data[0:4])
                break
    # print(data_dict)

    # 开始根据数据画图
    tm = Template(open(os.path.join(os.path.dirname(__file__), 'render_template.html'), 'r').read())
    with open('git_static.html', 'w') as f:
        f.write(tm.render(data_list=data_list, dimensions=dimensions, date_list=date_list, datas_day=list(data_dict.values()), dimensions_day=dimensions_day, users=[key for key in data_dict]))
