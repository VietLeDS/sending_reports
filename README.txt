Các file cần chạy:
Ngày thường:
send_vol_9_at_09_00
send_vol__at_12_00
send_vol__at_14_00
send_vol__at_17_00
send_vol_20_at_20_00

send_vol_cn_at_10_00
send_vol_cn_at_16_00

send_lm12_gtsc_at_10_00
send_lm12_at_12_00

send_lm20_at_16_40
send_lm20_at_19_00

send_gtsc_at_21_00
send_lmc_at_21_15
Reco.bat

Event:
send_vol_9_at_09_00
send_vol_lm12_gtsc_at_10_00
send_vol__at_11_00
send_vol_lm12_at_12_00
send_vol__at_13_00
send_vol__at_14_00
send_vol__at_15_00
send_vol__at_16_00
send_vol__at_17_00
send_vol__at_18_00
send_vol_lm20_at_19_00
send_vol_20_at_20_00

send_vol_cn_at_10_00
send_vol_cn_at_16_00

send_lm20_at_16_40

send_gtsc_at_21_00
send_lmc_at_21_15
Reco.bat

Cách file chạy:
Process:
Bat file -(list of command)> gui.py -(call and schedule)> library_gui_ver2.py (included run redash code)
list of command = task, list_options
task = vol, lm20, lm12, gtsc, lmc
list_options = t (test), o (once), q (quick - not run redash) and other specific options depend on each task