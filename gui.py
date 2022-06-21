# import usually use library
import datetime
import logging
import pandas
import pyautogui
import numpy as np
import threading
# Work with clipboard
import pyperclip
import time
import win32clipboard
from PIL import Image
from io import BytesIO
from logging import info, critical
import pywinauto
from pywinauto import Application, Desktop
import sys
from data_collectors import run_query, run_multi_query
from Run_LM_v2 import run_lm_slot_2
from LM_Control import run_lm_control

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.CRITICAL)

# Requisites - a customized pbi file with:
# 1. No scroll bar
# 2. Some space to show "..." button on the screen

# Parameters list
# 1. About pbi file - program_path is different between each pc
# program_path = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
# program_path = r"C:\Users\ntphu\AppData\Local\Microsoft\WindowsApps\PBIDesktopStore.exe"
program_path = r"C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.105.1143.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe"
pbi_path = r"G:\My Drive\Ninjavan Project\Dataset\Daily Task for tool.pbix"
pbi_name = "Daily Task for tool - Power BI Desktop"
# 2. List report
col_list = ['report', 'page_name', 'caption', 'report_name', 'x1', 'y1', 'x2', 'y2']
df_report = pandas.read_csv('pbi_report_data.csv', low_memory=False, index_col='report', usecols=col_list)
export_path = r"G:\My Drive\Ninjavan Data\Fleet\Bot data"
# 3. Channel
zalo_GTSC = "HN DP GTSC"
zalo_FM = "OPEX - DP : First Mile"
zalo_LM = "OPEX - DP : Last Mile"
zalo_Cloud = "Cloud của tôi"
chat_test = "Just a little test"
chat_vol = "Dự Báo Vol Pickup - Deli : Fleet - WH"
browser_list = ['Google Chrome', 'Edge']
# 4. Position
zalo_send_file_button_position = (533, 959)
box_gg_chat = (1037, 969)
box_zalo_web = (987, 1014)
# 5. PBI web link
DAILY_TASK_LINK = r'https://app.powerbi.com/groups/me/datasets/f3eae8fe-1174-46b0-a35a-aad7516afb31/details'
DATASET_FLEET_LINK = r'https://app.powerbi.com/groups/me/datasets/8c81cf81-5b46-4bea-9f05-c7b50ba906fb/details'


# A part - general features
def get_running_windows():
    windows = Desktop(backend="uia").windows()
    return [w.window_text() for w in windows]


def open_browser():
    global browser_name
    # Browser always opens
    for name in browser_list:
        try:
            browser = Application(backend="uia").connect(title_re=f".*{name}.*", timeout=5, found_index=0).window(title_re=f".*{name}.*", found_index=0)
            browser.restore().maximize()
            browser_name = name
            break
        except pywinauto.findwindows.ElementNotFoundError:
            lst = get_running_windows()
            for _ in lst:
                if name in _:
                    browser = Application(backend="uia").connect(title=f"{_}", timeout=5, found_index=0).window(title=f"{_}", found_index=0)
                    browser.restore().maximize()
                    browser_name = name
                    break
    return browser


def open_pbi():
    # Open pbi file or connect exist one
    if pbi_name not in get_running_windows():
        Application(backend="uia").start(f'{program_path} "{pbi_path}"', timeout=20)
        time.sleep(20)
    pbi = Application(backend="uia").connect(title=pbi_name, timeout=5).window(title=pbi_name)
    return pbi


def set_up():
    global pbi
    global browser
    print('You have been runned')
    pbi = open_pbi()
    browser = open_browser()


# Function 1 to screenshot and send to the clipboard
def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()


# Function 2 to screenshot and send to the clipboard
def screenshot_to_clipboard(position):
    image = pyautogui.screenshot(region=position)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    send_to_clipboard(win32clipboard.CF_DIB, data)
    time.sleep(1)


# Get position of an Element
def get_position(w):
    str_ = str(w.rectangle())
    str_ = str_.replace('(', '').replace(')', '')
    list_ = str_.split(',')
    for _, _v in enumerate(list_):
        list_[_] = int(list_[_].strip()[1:])
    x = int((list_[0] + list_[2]) / 2)
    y = int((list_[1] + list_[3]) / 2)
    return [x, y]


# B part - duplicate code, specific functions
def open_tab(tab='chat', channel=None):

    if tab == 'chat':
        key = 'Chat'
        link = 'https://mail.google.com/chat'
    elif tab == 'zalo':
        key = 'Zalo'
        link = 'https://chat.zalo.me/'
    else:
        return None

    browser.maximize()
    time.sleep(1)
    pyautogui.hotkey('ctrl', '1')  # Tránh 1 lỗi
    time.sleep(1)

    try:  # If there is one window's name contains "chat"
        browser.child_window(title_re=f".*{key}.*", control_type="TabItem", found_index=0).click_input()  # Click tab chat
    except:  # Open a new chat
        browser.child_window(title="New Tab", control_type="Button").click_input()  # Open new tab
        time.sleep(0.5)
        pyperclip.copy(link)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.hotkey('enter')
        time.sleep(10)  # Wait tab

    # Open channel in other environments
    if channel is not None and tab == 'chat' and browser_name == 'Edge':
        browser.child_window(title="Just a little test Space Pinned conversation Press tab for more options.", control_type="Hyperlink").click_input()
    elif channel is not None and tab == 'chat' and browser_name == 'Google Chrome':
        browser.child_window(title=channel, control_type='Text', found_index=0).click_input()
    elif channel is not None and tab == 'zalo':
        browser[channel].click_input()


def zalo_click_send_file_button():
    # Zalo has already been opened
    time.sleep(1)
    for _ in range(10):
        pyautogui.click(zalo_send_file_button_position)
        time.sleep(0.5)  # Don't too fast
        try:
            browser.child_window(title='Chọn File', control_type="Text", found_index=0).click_input()
            break
        except pywinauto.findwindows.ElementNotFoundError:
            try:
                print('First option fail')
                browser.child_window(title='Chọn tập tin', control_type="Text", found_index=0).click_input()
                break
            except pywinauto.findwindows.ElementNotFoundError:
                print('Second option fail')
                continue


# Refresh data in pbi
def pbi_refresh_data():
    pbi.maximize()
    pbi.child_window(title="Home", control_type="TabItem", found_index=0).click_input()  # Click Home Tab
    pbi.child_window(title="Refresh", control_type="Button", found_index=0).click_input()  # Python finds out 3 refresh buttons but just the first is true
    run_time_start = datetime.datetime.now()
    # for i in range(120):  # try in about 18 minutes
    while True:
        try:
            pbi.child_window(title="Close", control_type="Button", found_index=1).click_input()  # Refresh success -> there are 2 close buttons
            time.sleep(3)  # Founded -> wait 3s -> click
            info("Refresh success")
            return True
        except:
            cur_time = datetime.datetime.now()
            time_diff = (cur_time - run_time_start).total_seconds()
            if time_diff <= 20*60:
                continue
            else:
                info("Refresh fail")
                pbi.child_window(title="Close", control_type="Button", found_index=0).click_input()  # Close refresh
                return False


def pbi_web_refresh(link):
    try:
        set_up()
        browser.restore().maximize()
        browser.NewTabButton.click_input()
        pyperclip.copy(f'{link}')
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('enter')
        browser.child_window(title='Refresh').click_input()
        browser.child_window(title='Refresh now').click_input()
    except:
        pass


def export_data_pbi(key):
    if df_report.loc[key]['report_name'] is np.nan:
        return None

    page_name = df_report.loc[key]['page_name']
    report_name = df_report.loc[key]['report_name']

    pbi.maximize()
    pbi.child_window(title=page_name, control_type='TabItem').click_input()
    # Click report to show "..." button
    x = pbi.child_window(title_re=report_name, control_type="Group", found_index=0)
    x.click_input()
    time.sleep(0.5)
    x.click_input()
    x.child_window(title="More options", found_index=0).click_input()
    pbi.child_window(title="Export data", control_type="MenuItem").click_input()
    time.sleep(5)  # wait the dialog to show
    pyperclip.copy(f'{export_path}\{report_name}.csv')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pbi.child_window(title="Save As", control_type="Window").child_window(title="Save", control_type="Button",
                                                                          found_index=0).click_input()
    try:
        pbi.child_window(title="Confirm Save As", control_type="Window").child_window(title="Yes",
                                                                                      auto_id="CommandButton_6",
                                                                                      control_type="Button").click_input()
    except:
        pass
    # convert_to_excel(report_name)


def convert_to_excel(filename):
    pandas.read_csv(f'{export_path}/{filename}.csv', low_memory=False).to_excel(f'{export_path}/{filename}.xlsx', index=False, engine='openpyxl')


# Clear message box
def clear_message_box(tab='chat', channel=None):

    if tab == 'chat':
        key = f'Message {channel}'
        position = box_gg_chat
    elif tab == 'zalo':
        key = 'Nhập @'
        position = box_zalo_web
    else:
        return None
    
    try: # Khi message box không có chữ
        browser.child_window(title_re=f'^{key}.*', found_index=0).click_input()
    except: # Khi message box có chữ
        pyautogui.moveTo(position)
        time.sleep(0.25)
        pyautogui.click()
        time.sleep(0.25)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.25)
        pyautogui.hotkey('delete')
        time.sleep(0.25)


# Tag all
def tag_all():
    time.sleep(0.5)
    pyautogui.write('@')
    time.sleep(0.5)
    pyautogui.write('all')
    time.sleep(2)
    pyautogui.hotkey('Tab')
    time.sleep(0.5)


# Send Report
def send_report(key):
    # cursor has already been in the message bot
    today_str = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y")
    if df_report.loc[key]['caption'] is not np.nan:
        pyperclip.copy(df_report.loc[key]['caption'] + today_str)
        pyautogui.hotkey('ctrl', 'v')

    pbi.maximize()
    pbi.child_window(title=df_report.loc[key]['page_name'], control_type='TabItem').click_input()
    time.sleep(3) # Wait pbi to load report
    x1 = df_report.loc[key]['x1']
    y1 = df_report.loc[key]['y1']
    x2 = df_report.loc[key]['x2']
    y2 = df_report.loc[key]['y2']
    screenshot_to_clipboard((x1, y1, x2-x1, y2-y1))

    # Paste to message box
    browser.maximize()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(10)  # Wait image to load
    pyautogui.hotkey('enter')
    time.sleep(3)
    # cursor end in the message box


# Send data file
def send_data_to_zalo(key):
    browser.maximize()
    zalo_click_send_file_button()
    time.sleep(2)  # Wait the dialog
    if isinstance(key, str):        
        text = f'{export_path}\ {df_report.loc[key]["report_name"]}.csv'
    elif isinstance(key, list):
        text = f'{export_path}\ '
        for _ in key:
            text += f'"{df_report.loc[_]["report_name"]}.csv" '
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)  # Don't too fast
    pyautogui.hotkey('enter')


# C part - flow codes
def send_vol_to_gg_chat(channel=chat_vol, refresh=True, send_lm_speed=True, send_vol_lm=False):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='chat', channel=channel)
        clear_message_box(tab='chat', channel=channel)
        tag_all()
        send_report('vol')
        try:  # Click Send now button when tag all in ggchat
            browser.child_window(title="Send now", control_type="Button").click_input()
        except:
            pass
        info("Done vol 1")

        send_report('vol3')
        send_report('vol2')

        if send_lm_speed:
            send_report('lmspeed')

        if send_vol_lm:
            send_report('vollm')


# Function 3 in GTSC - Thao tác trên zalo
def send_gtsc_to_zalo(channel=zalo_GTSC, refresh=True, gtsc_10h=False):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='zalo', channel=channel)
        clear_message_box(tab='zalo')
        if channel != zalo_Cloud and channel != zalo_LM:
            tag_all()

        # Send image
        send_report('gtsc')
        if not gtsc_10h:
            send_report('gtsc2')
            send_report('gtsc3')

        # Export data
        export_data_pbi('gtsc')
        if not gtsc_10h:
            export_data_pbi('gtsc2')
            export_data_pbi('gtsc3')

        # Send data file to zalo
        if not gtsc_10h:
            send_data_to_zalo(['gtsc', 'gtsc2', 'gtsc3'])
        else:
            send_data_to_zalo('gtsc')


def send_fm_to_zalo(channel=zalo_FM, refresh=True):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='zalo', channel=channel)
        clear_message_box(tab='zalo')
        if channel != zalo_Cloud and channel != zalo_LM:
            tag_all()

        # Send image
        send_report('fm')

        # Export data
        export_data_pbi('fmdetail')

        # Send data file to zalo
        send_data_to_zalo('fmdetail')


def send_lm_to_zalo(channel=zalo_LM, refresh=True):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='zalo', channel=channel)
        clear_message_box(tab='zalo')
        if channel != zalo_Cloud and channel != zalo_LM:
            tag_all()

        # Send image
        send_report('lm')

        # Export data
        export_data_pbi('lmdetail')

        # Send data file to zalo
        send_data_to_zalo('lmdetail')


def send_lm_control_to_zalo(channel=zalo_LM, refresh=True):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='zalo', channel=channel)
        clear_message_box(tab='zalo')
        if channel != zalo_Cloud and channel != zalo_LM:
            tag_all()

        # Send image
        send_report('lmc')

        # Export data
        export_data_pbi('lmcdetail')

        # Send data file to zalo
        send_data_to_zalo('lmcdetail')


def send_lm_12h_to_zalo(channel=zalo_LM, refresh=True):
    set_up()
    ref = pbi_refresh_data() if refresh else True
    if not ref:
        critical("Refresh fail, Dont send")
    else:
        open_tab(tab='zalo', channel=channel)
        clear_message_box(tab='zalo')
        if channel != zalo_Cloud and channel != zalo_LM:
            tag_all()

        # Send image
        send_report('lm12')


# D part - wrap with command_list
def send_vol(refresh=True, send_lm_speed=True, send_vol_lm=False, channel=chat_vol, collect_data=True, command=None):
    print(f'Start send vol, command = {command}')
    today = datetime.date.today()
    list_redash = [[19767, 'LMFN api'], [13798, 'Pending PU'], [14881, 'Inventory'], [13671, 'FMFN API']]

    if command is not None:
        # optional command
        if 'q' in command:
            collect_data = False
        if '9' in command:
            send_lm_speed = False
            list_redash = [[13798, 'Pending PU'], [13671, 'FMFN API']]
        if '20' in command:
            send_vol_lm = True

        # end command
        if 't' in command:
            send_vol_to_gg_chat(channel=chat_test, refresh=False, send_lm_speed=True, send_vol_lm=True)
            print('Test done')
            return None
        elif 'cn' in command:
            send_lm_speed = False
            list_redash = [[13798, 'Pending PU'], [13671, 'FMFN API']]
            if today.weekday() != 6:
                return None
        else:
            if today.weekday() == 6:
                return None

    if collect_data:
        run_multi_query(list_redash)
    print('prepare to ref and send')
    pbi_web_refresh(DAILY_TASK_LINK)
    send_vol_to_gg_chat(channel=channel, refresh=refresh, send_lm_speed=send_lm_speed, send_vol_lm=send_vol_lm)


def send_gtsc(channel=zalo_GTSC, refresh=True, collect_data=True, gtsc_10h=False, command=None):
    print(f'Start send gtsc, command = {command}')
    today = datetime.date.today()
    list_redash = [[19767, 'LMFN api'], [14200, 'GTSC'], [13798, 'Pending PU'], [15553, 'Transit HCM - HN'],
                   [14881, 'Inventory'], [19396, 'GTSC North'], [13671, 'FMFN API']]

    if command is not None:
        # optional command
        if 'q' in command:
            collect_data = False
        if 'gtsc10' in command:
            gtsc_10h = True

        # end command
        if 't' in command:
            send_gtsc_to_zalo(channel=zalo_Cloud, refresh=False, gtsc_10h=gtsc_10h)
            return None
        else:
            if today.weekday() == 6:
                return None

    if collect_data:
        run_multi_query(list_redash)
    pbi_web_refresh(DAILY_TASK_LINK)
    send_gtsc_to_zalo(channel=zalo_GTSC, refresh=refresh, gtsc_10h=gtsc_10h)


def send_lm20(channel=zalo_LM, refresh=True, collect_data=True, command=None):
    print(f'Start send lm20, command = {command}')
    today = datetime.date.today()

    if command is not None:
        # optional command
        if 'q' in command:
            collect_data = False

        # end command
        if 't' in command:
            send_lm_to_zalo(channel=zalo_Cloud, refresh=False)
            return None
        else:
            if today.weekday() == 6:
                return None

    if collect_data:
        lm = run_lm_slot_2(detail=True)
        if lm:
            pbi_web_refresh(DAILY_TASK_LINK)
            send_lm_to_zalo(channel=zalo_LM, refresh=refresh)
    else:
        pbi_web_refresh(DAILY_TASK_LINK)
        send_lm_to_zalo(channel=zalo_LM, refresh=refresh)


def send_lm12(channel=zalo_LM, refresh=True, collect_data=True, command=None):
    print(f'Start send lm12, command = {command}')
    today = datetime.date.today()
    list_redash = [[19767, 'LMFN api'], [13798, 'Pending PU'], [14881, 'Inventory'], [13671, 'FMFN API']]

    if command is not None:
        # optional command
        if 'q' in command:
            collect_data = False

        # end command
        if 't' in command:
            send_lm_12h_to_zalo(channel=zalo_Cloud, refresh=False)
            return None
        else:
            if today.weekday() == 6:
                return None

    if collect_data:
        run_multi_query(list_redash)
    pbi_web_refresh(DAILY_TASK_LINK)
    send_lm_12h_to_zalo(channel=zalo_LM, refresh=refresh)


def send_lmc(channel=zalo_LM, refresh=True, collect_data=True, command=None):
    print(f'Start send lmc, command = {command}')
    today = datetime.date.today()
    if command is not None:
        # optional command
        if 'q' in command:
            collect_data = False

        # end command
        if 't' in command:
            send_lm_control_to_zalo(channel=zalo_Cloud, refresh=False)
            return None


    if collect_data:
        lm = run_lm_control()
        if lm:
            pbi_web_refresh(DAILY_TASK_LINK)
            send_lm_control_to_zalo(channel=zalo_LM, refresh=refresh)
    else:
        pbi_web_refresh(DAILY_TASK_LINK)
        send_lm_control_to_zalo(channel=zalo_LM, refresh=refresh)


def call_func(name_list, *args, **kwargs):
    if len(name_list) == 1:
        globals()[f'send_{name_list[0]}'](*args, **kwargs)
    else:
        for _ in name_list:
            globals()[f'send_{_}'](*args, **kwargs)
