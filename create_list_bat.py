# create a lot of bat file
list_of_command = {'t': 'test', 'o': 'once', 's': 'schedule', 'q': 'quick'}
list_code = ['vol', 'lm20', 'lm12', 'lmc', 'gtsc']
schedule_dict = {'vol': {'normal': [f'{str(h).zfill(2)}:00' for h in range(10, 20)],
						 '9': ['09:00'],
						 '20': ['20:00'],
						 'cn': ['10:00', '16:00']},
				 'gtsc': ['10:00', '21:00'],
				 'lm20': ['16:40', '19:00'],
				 'lm12': ['10:00', '12:00'],
				 'lmc': ['21:15']}

all_time_run = {}
for i in list_code:
	if not isinstance(schedule_dict[i], dict):
		for j in schedule_dict[i]:
			all_time_run[j] = []
	else:
		for subtype in schedule_dict[i].keys():
			for j in schedule_dict[i][subtype]:
				all_time_run[j] = []

for i in list_code:
	if not isinstance(schedule_dict[i], dict):
		for j in schedule_dict[i]:
			all_time_run[j].append(i)
	else:
		for subtype in schedule_dict[i].keys():
			for j in schedule_dict[i][subtype]:
				if subtype == 'normal':
					all_time_run[j].append(i)
				else:
					all_time_run[j].append(f'{i}_{subtype}')

print(all_time_run)

# Clear old bat file
import os
lst = [f for f in os.listdir() if '.bat' in f and 'send' in f]
for _ in lst:
	os.remove(_)

# Create not schedule code
for code in list_code:
	for run_type in list_of_command.keys():
		if run_type != 's':
			if not isinstance(schedule_dict[code], dict):
				with open(f'send_{code}_{list_of_command[run_type]}.bat', 'w') as f:
					f.write(f'TITLE send_{code}_{run_type}\npython tasks.py {code} {run_type}\nPAUSE')
			else:
				for subtype in schedule_dict[code].keys():
					with open(f'send_{code}_{subtype}_{list_of_command[run_type]}.bat', 'w') as f:
						f.write(f'TITLE send_{code}_{subtype}_{run_type}\npython tasks.py {code} {subtype} {run_type}\nPAUSE')

# Create single schedule code
for code in schedule_dict.keys():
	if not isinstance(schedule_dict[code], dict):
		for time in schedule_dict[code]:
			with open(f'send_{code}_at_{time.replace(":","_")}.bat', 'w') as f:
				f.write(f'TITLE send_{code}_{time}\npython tasks.py {code} s {time}\nPAUSE')
	else:
		for subtype in schedule_dict[code].keys():
			for time in schedule_dict[code][subtype]:
				if subtype == 'normal':
					subtype = ''
				with open(f'send_{code}_{subtype}_at_{time.replace(":","_")}.bat', 'w') as f:
					f.write(f'TITLE send_{code}_{subtype}_{time}\npython tasks.py {code} {subtype} s {time}\nPAUSE')


# Create multi schedule code
for hour in all_time_run.keys():
	if len(all_time_run[hour]) > 1:
		name1 = '_'.join(all_time_run[hour])
		name2 = ' '.join(all_time_run[hour])
		with open(f'send_{name1}_at_{hour.replace(":","_")}.bat', 'w') as f:
			f.write(f'TITLE send_{name1}_{hour}\npython tasks.py {name2} s {hour}\nPAUSE')
