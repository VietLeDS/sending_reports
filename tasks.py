import sys, time

import schedule

sys.path.append(r'G:\My Drive\Ninjavan Project\Python code')
import gui as g

list_code = ['vol', 'lm20', 'lm12', 'lmc', 'gtsc']


def run(lst):
    _list_code = [c for c in lst if c in list_code]
    print(f'list_code = {_list_code}')
    if 's' not in lst:
        g.call_func(_list_code, command=lst)
    else:
        for _ in lst:
            if ":" in _:
                run_time = _

        schedule.every().day.at(f"{run_time}").do(g.call_func, _list_code, command=lst)

        while True:  # 7 ngày bảo trì 1 lần
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    # import os
    # import datetime

    # with open(r'H:\My Drive\Viet_Project\PythonProject\runHistory.csv', 'a') as f0:
    #     now = datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d_%H_%M_%S")
    #     f0.write(f'{now},{os.getpid()},{__file__}\n')
    #     print(f'{now},{os.getpid()},{__file__}\n')

    run(sys.argv)
