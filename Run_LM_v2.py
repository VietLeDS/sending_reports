import sys
import threading
import datetime
from datetime import timedelta, date
from logging import critical

import pandas as pd

from data_collectors import run_query

# set up
path_fmfn = r'G:\My Drive\Ninjavan Data\Fleet\Firstmile\FirstMile _ Final'
path_write = r'G:\My Drive\Ninjavan Data\Fleet\Daily Task\LM\Push LM evening'
user_api_key = 'DWfgsukoVVY3vSafuAcqh8ZxA1dlQZcjhsCzZklP'

lock = threading.Lock()


def read_fm(ro, date_str):
    if date_str not in ('2022-05-01', '2022-04-30'):
        return pd.read_csv(f'{path_fmfn}/OPEX_HN_-_Firstmile_Final_{date_str}.csv',
                           low_memory=False, usecols=ro.fnfn_columns)
    else:
        return pd.DataFrame(columns=ro.fnfn_columns)


class RunOptions:
    def __init__(self, detail=False):
        if detail:
            critical("Start")
        self.start = datetime.datetime.now()
        self.end = None

        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.two_days_b4 = self.today - timedelta(days=2)
        self.three_days_b4 = self.today - timedelta(days=3)

        self.today_str = f'{self.today.year}_{str(self.today.month).zfill(2)}_{str(self.today.day).zfill(2)}'
        self.yesterday_str = f'{self.yesterday.year}_{str(self.yesterday.month).zfill(2)}_{str(self.yesterday.day).zfill(2)}'
        self.two_days_b4_str = f'{self.two_days_b4.year}_{str(self.two_days_b4.month).zfill(2)}_{str(self.two_days_b4.day).zfill(2)}'
        self.three_days_b4_str = f'{self.three_days_b4.year}_{str(self.three_days_b4.month).zfill(2)}_{str(self.three_days_b4.day).zfill(2)}'
        self.detail = detail

        self.inventory_id = 14881
        self.inventory_split_id = [19787, 19788, 19789]
        self.last_scan_id = 19884

        # self.nshopee_path1 = r'G:\My Drive\Ninjavan Data\Fleet\Daily Task\NonShopee Slot 2'
        # self.nshopee_path2 = r'G:\My Drive\Ninjavan Data\Fleet\Daily Task\Metabase auto code'

        self.col_list_export = ['order_id', 'tracking_id', 'first_txn_priority_level', 'status', 'granular_status',
                                'rts',
                                'last_attempt', 'route_name', 'route_id', 'last_hub', 'dest_hub', 'Check_hub',
                                'shipper_group',
                                'pickup_region', 'pickup_scan_at', '1st_scan_last_hub']
        self.Inven_col_list = ['day_since_reach_last_hub', 'first_reach_last_hub_at', 'order_id', 'granular_status',
                               'rts',
                               'order_tags', 'shipper_id', 'shipper_name', 'service_type', 'last_scan_hub',
                               'check_date',
                               'txn_status', 'order_value', 'instruction', 'SIZE', 'ten_khach', 'sdt_khach',
                               'dia_chi_khach',
                               'insurance', 'goods_value', 'cod', 'lsh_fail_attempt']
        self.fnfn_columns = ['order_id', 'granular_status', 'order_value', 'shipper_id', 'shipper', 'pickup_hub',
                             'pickup_route_name', 'pickup_scan_type', 'pickup_scan_at', 'inbound_pickup_hub_at',
                             'pickup_add_shipment_at', 'shipment_receive_at', 'hub_inb_at', 'sort_at',
                             'add_shipment_at',
                             'shipment_id', 'shipment_dest_hub', 'dest_zone_hub', 'attempt_same_day', 'create_datetime',
                             'Shipper_Submitted_length_cm', 'Shipper_Submitted_width_cm', 'Shipper_Submitted_height_cm',
                             'Shipper_Submitted_Weight', 'length_cm', 'width_cm', 'height_cm', 'weight']


def get_data_inventory(ro, run_non_shopee=False):
    # # Get data from code split
    # df_export = [thread_export() for _ in range(3)]
    # thread = {
    #     "thread_{0}".format(i): threading.Thread(
    #         target=run_query,
    #         args=(ro.inventory_split_id[i],),
    #         kwargs={
    #             'col_list': ro.Inven_col_list,
    #             'detail': ro.detail,
    #             'df_export': df_export[i],
    #         },
    #     )
    #     for i in range(3)
    # }

    # for nr in range(3):
    #     thread["thread_{0}".format(nr)].start()
    # for nr in range(3):
    #     thread["thread_{0}".format(nr)].join()

    # df_inven = pd.concat([df_export[_].df for _ in range(3)])

    df_inven = run_query(ro.inventory_id, col_list=ro.Inven_col_list, detail=ro.detail)

    # Transform data
    df_inven['first_reach_last_hub_at'] = pd.to_datetime(df_inven['first_reach_last_hub_at'])
    df_inven = df_inven[(df_inven['txn_status'] == 'Pending')]

    df_inven['shipper_group'] = pd.NaT
    for _ in df_inven.index:
        if isinstance(df_inven.loc[_, 'shipper_name'], str):
            df_inven.loc[_, 'shipper_group'] = df_inven.loc[_, 'shipper_name'][:6]

    # 1st scan trước 16h ngày N với đơn Shopee (thứ 2 cũng thế)
    df_inven_1 = df_inven[(
            (df_inven['shipper_group'] == "Shopee")
            & (df_inven['first_reach_last_hub_at'] < f'{ro.today_str.replace("_", "-")} 16:00:00')
    )]
    df_inven0 = df_inven_1

    # Từ tháng 5.2022, không push Non Shopee trong task này nữa
    # # Không lấy đơn Non Shopee trừ khi metabase không chạy được
    # if run_non_shopee:
    #     print(f"Num of Non Shopee before filter is {len(df_inven[(df_inven['shipper_group'] != 'Shopee')])}")
    #     # 1st scan trc 12h ngày N-1, N-2 với thứ hai Non Shopee
    #     if ro.today.weekday() == 0:  # If monday
    #         df_inven_2 = df_inven[(
    #                 (df_inven['shipper_group'] != "Shopee")
    #                 & (df_inven['first_reach_last_hub_at'] < f'{ro.two_days_b4_str.replace("_", "-")} 12:00:00')
    #         )]
    #     else:
    #         df_inven_2 = df_inven[(
    #                 (df_inven['shipper_group'] != "Shopee")
    #                 & (df_inven['first_reach_last_hub_at'] < f'{ro.yesterday_str.replace("_", "-")} 12:00:00')
    #         )]
    #     df_inven0 = pd.concat([df_inven0, df_inven_2])
    #     print(f'Num of Non Shopee Intra = {len(df_inven_2)}')
    #     del df_inven_2

    if ro.detail:
        critical(f'Get data from inventory, len = {len(df_inven0)}')
    return df_inven0[['order_id']]


def get_data_fmfn(ro, run_non_shopee=False):
    # Get data
    if ro.today.weekday() == 0:  # If monday
        df_FMFN1 = read_fm(ro, ro.yesterday_str)
        df_FMFN2 = read_fm(ro, ro.two_days_b4_str)
        df_FMFN3 = read_fm(ro, ro.three_days_b4_str)
    else:
        df_FMFN1 = read_fm(ro, ro.yesterday_str)
        df_FMFN2 = read_fm(ro, ro.two_days_b4_str)
        df_FMFN3 = pd.DataFrame(columns=ro.fnfn_columns)

    # Transform
    df_FMFN = pd.concat([df_FMFN1, df_FMFN2, df_FMFN3])
    df_FMFN['pickup_scan_at'] = pd.to_datetime(df_FMFN['pickup_scan_at'])
    del df_FMFN1, df_FMFN2, df_FMFN3

    df_FMFN = df_FMFN[((df_FMFN['pickup_hub'] == df_FMFN['dest_zone_hub'])
                       & (df_FMFN['granular_status'] != 'Completed')
                       & (df_FMFN['granular_status'] != 'Cancelled') & (
                               df_FMFN['granular_status'] != 'Returned to Sender'))]

    df_FMFN['shipper_group'] = pd.NaT
    for _ in df_FMFN.index:
        if isinstance(df_FMFN.loc[_, 'shipper'], str):
            df_FMFN.loc[_, 'shipper_group'] = df_FMFN.loc[_, 'shipper'][:6]

    # đơn intra hub pickup ngày N-1 trc 16h đối với đơn Shopee (thứ 2 là N-2)
    if ro.today.weekday() == 0:  # If monday
        df_FMFN_1 = df_FMFN[(
                (df_FMFN['shipper_group'] == "Shopee")
                & (df_FMFN['pickup_scan_at'] < f'{ro.two_days_b4_str.replace("_", "-")} 16:00:00')
        )]
    else:
        df_FMFN_1 = df_FMFN[(
                (df_FMFN['shipper_group'] == "Shopee")
                & (df_FMFN['pickup_scan_at'] < f'{ro.yesterday_str.replace("_", "-")} 16:00:00')
        )]
    df_FMFN0 = df_FMFN_1
    del df_FMFN_1

    # Từ tháng 5.2022, không push Non Shopee trong task này nữa
    # # Không lấy đơn Non Shopee trừ khi metabase không chạy được
    # if run_non_shopee:
    #     # đơn intra hub pickup ngày N-2 trc 12h đối với đơn Non Shopee (thứ 3 là N-3)
    #     if ro.today.weekday() == 1:  # If tuesday
    #         df_FMFN_2 = df_FMFN[(
    #                 (df_FMFN['shipper_group'] != "Shopee")
    #                 & (df_FMFN['pickup_scan_at'] < f'{ro.three_days_b4_str.replace("_", "-")} 12:00:00')
    #         )]
    #     else:
    #         df_FMFN_2 = df_FMFN[(
    #                 (df_FMFN['shipper_group'] != "Shopee")
    #                 & (df_FMFN['pickup_scan_at'] < f'{ro.two_days_b4_str.replace("_", "-")} 12:00:00')
    #         )]
    #     df_FMFN0 = pd.concat([df_FMFN0, df_FMFN_2])
    #     print(f'Num of Non Shopee Intra = {len(df_FMFN_2)}')
    #     del df_FMFN_2

    if ro.detail:
        critical(f'Get data from FM, len = {len(df_FMFN0)}')

    return df_FMFN0[['order_id']]


def run_lm_slot_2(detail=False, run_non_shopee=False):
    # Step 1: Setup
    ro = RunOptions(detail=detail)

    # Step 2: Get data to run last scan
    df_inven_id = get_data_inventory(ro, run_non_shopee=run_non_shopee)
    df_FMFN_id = get_data_fmfn(ro, run_non_shopee=run_non_shopee)
    # df_nshopee_id = get_data_nshopee_slot_2(ro)
    data = pd.concat([df_inven_id, df_FMFN_id])  # , df_nshopee_id
    data.drop_duplicates()
    del df_inven_id
    del df_FMFN_id

    # Step 3: Run last scan
    df_export = run_query(ro.last_scan_id, df_input=data, col_list=ro.col_list_export, parameter='id', detail=ro.detail)

    # Step 4: Export and Replace old file
    df_export.to_csv(f'{path_write}/OPEX_HN_-_last_scan_(Phượng)_shortened_{ro.today_str}.csv', index=False)
    del df_export

    setattr(ro, 'end', datetime.datetime.now())
    critical(f'Done all, runtime = {ro.end - ro.start}')
    return True


# def get_data_nshopee_slot_2(ro):
#     df = pd.read_csv(f'{ro.nshopee_path2}/NonShopee Slot 2_{ro.today_str}.csv', low_memory=False)
#     # df = df[(df['first_valid_delivery_attempt_datetime'].isna())]
#     # # df = df[(~df['wh_outbound_at'].isna())]
#     # df = df[((df['granular_status'] != "Cancelled")
#     #          & (df['shipper_group'] != "Shopee Return Vietnam"))]
#     if ro.detail:
#         critical(f'Get data from NShopee, len = {len(df)}')
#     return df[['order_id']]


if __name__ == '__main__':
    # Code lấy PID của current file
    import os
    import datetime

    with open(r'H:\My Drive\Viet_Project\PythonProject\runHistory.csv', 'a') as f0:
        now = datetime.datetime.strftime(datetime.datetime.now(), "%Y_%m_%d_%H_%M_%S")
        f0.write(f'{now},{os.getpid()},{__file__}\n')
        print(f'{now},{os.getpid()},{__file__}\n')

    # Chạy test function, bình thường không chạy file này mà import hàm từ file này
    run_lm_slot_2(detail=True)
