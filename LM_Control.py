import datetime
import os
import schedule
import sys
import time
from logging import critical

import pandas as pd

sys.path.append(r'G:\My Drive\Ninjavan Data\Fleet\Daily Task\library_redash')
from library_redash_ninjavan import run_query

path = r'G:\My Drive\Ninjavan Data\Fleet\Inventory'
path_export = r'G:\My Drive\Ninjavan Data\Fleet\Daily Task\LM Control'
inventory_col_list = ['day_since_reach_last_hub', 'first_reach_last_hub_at', 'order_id', 'granular_status', 'rts',
                      'order_tags', 'shipper_id', 'shipper_name', 'service_type', 'last_scan_hub', 'check_date',
                      'txn_status', 'order_value', 'instruction', 'SIZE', 'lsh_fail_attempt', 'zone_deli_hub']

check_pull_out = 19712


def check_inventory():
    list_files = os.listdir(path)
    a = datetime.timedelta(-1)
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d")
    if f'Inventory_{today}.csv' in list_files:
        return f'Inventory_{today}.csv'
    else:
        return False


def run_lm_control():
    while True:
        check_time = datetime.datetime.now()
        if 20 < check_time.hour < 24:
            try:
                critical('Start run lm control')
                start = datetime.datetime.now()
                df = run_query(14881, col_list = inventory_col_list)
                df2 = run_query(19395, df_input=df[['order_id']], wait=0.5, detail=False)  # Check inbound after delivery fail
                # df3 = run_query(19712, df_input=df[['order_id']], wait=0.5, detail=False)  # Check pull out
                df2 = df2[['order_id', 'last_delivery_fail_at', 'first_inbound_after_fail_at', 'route_name']]
                # df3['Has pull out'] = pd.NaT
                # df3['Has pull out'] = df3['Has pull out'].fillna(1)
                df_merge = pd.merge(df, df2, on='order_id', how='left')
                # if len(df3):
                #     df_merge = pd.merge(df_merge, df3, on='order_id', how='left')
                #     df_merge.to_csv(f'{path_export}/{check_inventory()}', index=False)
                # else:
                #     df_merge['Has pull out'] = pd.NaT
                today = datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d")
                df_merge.to_csv(f'{path_export}/Inventory_{today}.csv', index=False)
                end = datetime.datetime.now()
                critical(f'Done all code run')
                del df, df2, df_merge, start, end
                return True
            except:
                print("Have not had data yet, wait 60sec")
                time.sleep(60)
