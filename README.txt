Các file bat cần chạy (.bat):

Ngày thường: (chạy file start_everything_nonev.bat để tự động bật các code bên dưới)
send_vol_at_09_00
send_vol_at_14_00
send_vol_at_17_00
send_vol_at_20_00
send_vol_cn_at_10_00
send_vol_cn_at_16_00
send_lm20_at_16_40
send_lm20_at_19_00
send_gtsc_at_21_00
send_lmc_at_21_15
send_lm12_gtsc_at_10_00
send_vol_lm12_at_12_00

Event:
send_vol_at_09_00
send_vol_at_11_00
send_vol_at_13_00
send_vol_at_14_00
send_vol_at_15_00
send_vol_at_16_00
send_vol_at_17_00
send_vol_at_18_00
send_vol_at_20_00
send_lm20_at_16_40
send_gtsc_at_21_00
send_lmc_at_21_15
send_vol_lm12_at_12_00
send_vol_lm20_at_19_00
send_vol_lm12_gtsc_at_10_00

Cách file chạy:
Process:
Bat file -(list of command)> gui.py -(call and schedule)> library_gui_ver2.py (included run redash code)
list of command = task, list_options
task = vol, lm20, lm12, gtsc, lmc
list_options = t (test), o (once), q (quick - not run redash) and other specific options depend on each task
