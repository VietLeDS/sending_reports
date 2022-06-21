import datetime
import json
import threading
import time

import pandas
import pandas as pd
import requests

user_api_key = 'DWfgsukoVVY3vSafuAcqh8ZxA1dlQZcjhsCzZklP'

import sys

lock = threading.Lock()


def query(ro, params=None, user_api_key=user_api_key):
    if params is None:
        params = {}
    run_num = 0

    while True:
        try:
            run_num += 1
            start = datetime.datetime.now()
            s = requests.Session()
            s.headers.update({'Authorization': f'Key {user_api_key}'})

            response = s.post(f'https://redash.ninjavan.co/api/queries/{ro.query_id}/refresh', params=params)

            if response.status_code != 200 and ro.detail:
                print(f'Refresh {ro.name} failed. status_code={response.status_code}. params={params}')
                continue

            if result_id := poll_job(s, response.json()['job']):
                response = s.get(f'https://redash.ninjavan.co/api/queries/{ro.query_id}/results/{result_id}.json')

                if response.status_code != 200:
                    if run_num == 1 and ro.detail:
                        print(f'{ro.name} Failed getting results. params={params}')
                    continue
            else:
                if run_num == 1 and ro.detail:
                    print(f'Query {ro.name} execution failed. params={params}')
                continue

            res = pd.DataFrame(response.json()['query_result']['data']['rows'])
            res.drop_duplicates(inplace=True)
            end = datetime.datetime.now()
            if ro.detail:
                print(f'Run {ro.name} success, result = {len(res.columns)} cols x {len(res)} rows, run_time={end - start}')
            return res
        except Exception as e:
            if run_num == 1 and ro.detail:
                print(f'Run {ro.name} fail, run again, exception = {e}')
            continue


def poll_job(s, job):
    start_poll = datetime.datetime.now()

    while job['status'] == 1:
        cur_poll_time = datetime.datetime.now()
        time_diff = (cur_poll_time - start_poll).total_seconds()
        if time_diff <= 360:
            response = s.get(f"https://redash.ninjavan.co/api/jobs/{job['id']}")
            job = response.json()['job']
            time.sleep(0.5)
            continue
        else:
            job['status'] = 4

    while job['status'] == 2:
        cur_poll_time = datetime.datetime.now()
        time_diff = (cur_poll_time - start_poll).total_seconds()
        if time_diff <= 3600:
            response = s.get(f"https://redash.ninjavan.co/api/jobs/{job['id']}")
            job = response.json()['job']
            time.sleep(0.5)
            continue
        else:
            job['status'] = 4

    if job['status'] == 3:
        return job['query_result_id']

    return None


def step_query(n, ro, params=None):
    if params is None:
        params = {}
    while True:
        try:
            df_ = query(ro=ro, params=params)
            if len(df_):
                if ro.col_list:
                    df_ = df_[ro.col_list]
                lock.acquire()
                ro.df_output = pd.concat([ro.df_output, df_])
                lock.release()
            break
        except Exception as e:
            time.sleep(1)
            print(f'{n} fail, exception = {e}\n')
            continue


class run_option(object):
    def __init__(self, **search_criteria):
        default_search_criteria = {'df_input': [], 'parameter': 'order_id',
                                   'extra_parameters': {}, 'split': 300, 'col_list': [], 'wait': 2,
                                   'name': '', 'detail': False, 'df_output': pandas.DataFrame(),
                                   'df_process': pandas.DataFrame()}

        for _ in default_search_criteria.keys():
            if _ not in search_criteria.keys():
                setattr(self, _, default_search_criteria[_])

        for _ in search_criteria.keys():
            setattr(self, _, search_criteria[_])

        self.clean_input()

    def clean_input(self):
        # convert data_type of df_input to list of int
        if isinstance(self.df_input, list):
            self.df_input = [int(float(f)) for f in self.df_input]
        elif isinstance(self.df_input, pandas.DataFrame):
            self.df_input = self.df_input.astype(int)
            self.df_input = list(self.df_input.iloc[:, 0])

    def get_parameter(self, x, y):
        converted_list = []
        if self.parameter in ['order_id', 'id', 'shipment_id']:
            converted_list = [str(element) for element in self.df_input[x:y]]
        elif self.parameter == 'tracking_id':
            converted_list = [f"'{str(element)}'" for element in self.df_input[x:y]]
        params_value = ",".join(converted_list)
        params = {f'p_{self.parameter}': f'{params_value}'}
        if self.extra_parameters:
            params.update(self.extra_parameters)
        return params

    def clean_output(self):
        if self.col_list:
            self.df_output = self.df_output[self.col_list]

    def query(self):
        self.df_output = query(self)
        self.clean_output()
        return self.df_output

    def get_output(self):
        self.clean_output()
        return self.df_output


def run_query(query_id, **kwargs):
    # Set up
    ro = run_option(query_id=query_id, **kwargs)

    # Run
    if len(ro.df_input):  # If run query with parameters
        if ro.detail:
            print(f"data length: {len(ro.df_input)}")

        # Split data and run thread query
        x, y, n = 0, ro.split, 1
        thread = {}
        while x < len(ro.df_input):
            thread["thread_{0}".format(n)] = threading.Thread(target=step_query,
                                                              args=(n, ro, ro.get_parameter(x, y)))
            n = n + 1
            x += ro.split
            y = y + ro.split
        if ro.detail:
            print(f'Starting threads, num_thread = {n - 1}')
        for nr in range(1, n):
            thread["thread_{0}".format(nr)].start()
            time.sleep(ro.wait)
        for nr in range(1, n):
            thread["thread_{0}".format(nr)].join()

        return ro.get_output()
    else:
        return ro.query()


def run_multi_query(Vol_Query_id=None):
    # all_code = [[19767, 'LMFN api'], [14200, 'GTSC'], [13798, 'Pending PU'], [15553, 'Transit HCM - HN'],
    #             [19789, 'Inventory split 1'], [19788, 'Inventory split 2'], [19787, 'Inventory split 3'],
    #             [19786, 'FMFN API split 4'], [19785, 'FMFN API split 3'], [19784, 'FMFN API split 2'],
    #             [19783, 'FMFN API split 1'], [19396, 'GTSC North'], [13671, 'FMFN API'], [17944, 'LMFN api old']]

    thread_runr = {}
    n = 1
    for Query_id in Vol_Query_id:
        thread_runr["thread_{0}".format(n)] = threading.Thread(target=run_query, args=(Query_id[0], ), kwargs={'name': Query_id[1], 'detail': True})
        n = n + 1
    for nr in range(1, n):
        thread_runr["thread_{0}".format(nr)].start()
    for nr in range(1, n):
        thread_runr["thread_{0}".format(nr)].join()
    print('Redash done all')


if __name__ == '__main__':
    run_redash([[13798, 'Pending PU'], [13671, 'FMFN API']])


