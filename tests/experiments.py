s = '0:19:43\n0:23:44\n0:50:54\n1:30:57\n1:40:20\n0:14:43\n0:21:46\n0:24:08\n0:35:31\n0:10:55\n2:09:50'
times = [[int(num_str) for num_str in time_str.split(':')] for time_str in s.split('\n')]
total_sec = sum([3600 * hr + 60 * min + sec for hr, min, sec in times])
hours = total_sec // 3600
minutes = (total_sec - hours * 3600) // 60
seconds = total_sec - hours * 3600 - minutes * 60
print(f'{hours} hours, {minutes} minutes, and {seconds} seconds')
