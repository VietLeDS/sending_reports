import os
import subprocess
import sys

path = r'G:\My Drive\Ninjavan Project\Python code'

list_normal = ['send_vol_cn_at_10_00', 'send_vol_cn_at_16_00', 'send_vol_9_at_09_00', 'send_vol__at_14_00',
               'send_vol__at_17_00', 'send_lmc_at_21_15', 'send_lm12_gtsc_at_10_00', 'send_gtsc_at_21_00',
               'send_vol_lm12_at_12_00', 'send_vol_20_at_20_00', 'send_lm20_at_16_40', 'send_lm20_at_19_00']

more_on_event = ['send_vol_lm12_gtsc_at_10_00', 'send_vol__at_11_00', 'send_vol__at_13_00', 'send_vol__at_15_00',
                 'send_vol__at_16_00', 'send_vol__at_18_00', 'send_vol_lm20_at_19_00']

list_event = list_normal + more_on_event

for a in ['send_lm12_gtsc_at_10_00', 'send_lm20_at_19_00']:
    list_event.remove(a)


def start_code(today_is):
    if today_is == 'nevent':
        for n in range(0, len(list_normal)):
            subprocess.Popen(f'{path}/{list_normal[n]}.bat', creationflags=subprocess.CREATE_NEW_CONSOLE)
    if today_is == 'event':
        for n in range(0, len(list_event)):
            subprocess.Popen(f'{path}/{list_event[n]}.bat', creationflags=subprocess.CREATE_NEW_CONSOLE)

start_code(sys.argv[1])