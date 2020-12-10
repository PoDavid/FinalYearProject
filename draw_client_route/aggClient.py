import os
import comlo
import argparse
from multiprocessing import Pool

all_field = { 	'time':0, # change the month name to a number
				'type':1,
				'IP':2,
				'hub':3,
				'client':4, # Mac address
				'conn_type':5, # jn (joins), dis (disconnected), rm (roamed), bk (backup), ch (change)
				'wifi_type':6, 
				'APID':7,
				'BSSID':8,
				'leave_reason_code':9, 
				'leave_APID':10, 
				'leave_BSSID':11,
				'leace_AC':12,
				'to_AC':13,
				'RadioId':14,
				'from_channel':15,
				'to_channel':16,
				'warning_type':17,
					# 'AP itf' : 'AP detected interfere' , 'chl itf' : Channel detected interfere , 'user dis' : User Disconnect,
					# 'STA itf' : Station detected interfere, 'STA dis': Station Disconnect
				'warning_code':18,
				'AP_Serial_Id':19,
				'APMAC':20,
				'STAMAC':21,
				'STAMAC2':22,
				'AP Name':23,
				'User name':24
			}

# ############################ˇ
# Global variables

enable_dis = True
dis_string = 'dis'
time_char = '-'
start_char = 's'
period_duration = 60
max_mac_num = 1000
track_pos = False

# Seriouly note that the time serie is acctually reversed,
# The front one is the latest, the back one is the earliests

# ############################
			
def collect_client_route( pro_csv, all_mac_dict ):

	for line in pro_csv:
		extract_from_line( line, all_mac_dict )

def time_pass(mac_dict_t):
	global track_pos
	for v in mac_dict_tf.values():
		if track_pos and v[1] == []:
			try:
				if v[0][-1] and not v[0][-1].endswith( dis_string ):
					v[1] = v[0][-1].split(time_char)
					if len(v[1]) > 1:
						v[1] = [ v[1][-1] ]
			except Exception as err:
				print( str(type(err)) + '\n' + str(err) + '\n' + v)

		v[0].append( time_char.join( v[1] ) )
		v[1] = []

def collect_client_route_seires( pro_csv, mac_dict_t, handled_mac_set ):
	'''
	Here I use ',' sign to distinguish the time period.
	this function generate the trace of a Mac, 
	that is, at which apid each Mac address is presented at each time period.
	'''
	global period_duration
	import time
	sec_count = period_duration - 1
	cur_time = None
	cur_step = -1

	for line in pro_csv:
		line_d = line.split(',')
		sec_change = comlo.time_change( cur_time, line )
		if sec_change:
			cur_time = line
			sec_count += sec_change
			
			while sec_count >= period_duration:
				time_pass(mac_dict_t)
				cur_step += 1
				sec_count -= period_duration
				
		extract_from_line_2(line_d , mac_dict_t, cur_step, handled_mac_set )

	time_pass(mac_dict_t)
		
def extract_from_line_2( line, mac_dict_t, cur_len, handled_mac_set ) -> int:
	'''
	mac_dict_t =
	{
		Mac : [ [past APID strings], [current APID] ]
	}
	'''
	global enable_dis, dis_string
	
	data = line.split(',') if isinstance( line, str ) else line
	
	# data[4] is the Mac address, please refer to the rawcsv.py
	mac_addr = data[4]

	if mac_addr not in handled_mac_set:
		return 2

	if data[5] == 'jn':
		temp_data = data[7]
		
	elif data[5] == 'dis':
		# if enable_dis id true, then dis should be added
		# if not, dis should be emitted for ease of analysis
		if enable_dis:
			temp_data = dis_string
		else:
			return 1

	elif data[5] == 'rm':
		if enable_dis:
			temp_data = [ data[7], dis_string ]
		else:
			temp_data = data[7]

	elif data[5] in [ 'bk', 'ch' ]:
		return 1
	else:
		print('unreognized data type.')
		raise Exception('unreognized data[5] in extract_from_line_2 : ' + str(data[5]) )
		
	try:
		if isinstance( temp_data, list ):
			mac_dict_t[ mac_addr ][1].extend( temp_data )
		else:	
			mac_dict_t[ mac_addr ][1].append( temp_data )
		#print(data[0])
		#print(mac_dict_t[ mac_addr ][1])
	except KeyError:
		mac_dict_t[ mac_addr ] = marrs( cur_len, temp_data )

	return 0
	
def marrs( cur_len, fornow ):
	fornow = [ fornow ] if not isinstance(fornow, list) else fornow
	if cur_len == 0:
		return [ [] , fornow ]

	return [ [','*cur_len] , fornow ]
	
def write_with_time( file_obj, mac_dict_t ):
	# have to join the APID for each time period, then join all the time period for that mac address
	# heavy operation, hope to improve
	for key in mac_dict_t.keys():
		'''
		print( mac_dict_t[key][0] )
		print( [ time_char.join(j) for j in mac_dict_t[key][0] ] )
		print( key + ':' + ','.join( [ time_char.join(j) for j in mac_dict_t[key][0] ] ) + '\n' )
		break
		'''

		long_str = ','.join( mac_dict_t[key][0] ) 
		file_obj.write( key + ':' + long_str + '\n' )
			
def collect_only_mac(folder_name):

	file_obj = comlo.terfread( folder_name )
	Mac_list = {}
	
	for line in file_obj:
		Mac = line.split(',')[4]
		
		if not Mac_list.get( Mac, False ):
			Mac_list[Mac] = True

	del Mac_list['']
	
	print(len(Mac_list))
	
	return list( Mac_list.keys() )

def aggFolderone( input_tuple ):
	folder_name, write_path, file_count, handled_mac_set = input_tuple
	all_mac_dict = {}
	pro_csv = comlo.terfread( folder_name )
	collect_client_route_seires( pro_csv, all_mac_dict, handled_mac_set )

	# write the result into the file
	# copatible with the comlo standard
	print(str(file_count) + ' writing')
	with open( write_path + '/' + str(file_count) + '.log', 'w' ) as routefile:
		write_with_time( routefile, all_mac_dict )
	
def aggFolder(folder_name, write_path):
	read_path = folder_name + '/infocsv'
	write_path = folder_name + write_path
	comlo.check_time_order(read_path)
	mac_distri = collect_only_mac(read_path)
	file_count = 0

	if not os.path.isdir( write_path ):
		os.makedirs( write_path )
	else:
		comlo.clean_dir( write_path )
	
	job_list = []
	
	while file_count*max_mac_num < len(mac_distri):
		if (file_count+1)*max_mac_num < len(mac_distri):
			handled_mac_set = frozenset( mac_distri[ file_count*max_mac_num : (file_count+1)*max_mac_num ] )
		else:
			handled_mac_set = frozenset( mac_distri[ file_count*max_mac_num : ] )
			
		job_list.append( ( read_path, write_path, file_count, handled_mac_set ) )

		file_count += 1

	with Pool(3) as porccess_pool:
		porccess_pool.map(aggFolderone, job_list)

		
def main():

	global track_pos

	# the structure of the mac dictionary
	# { key : client Mac , vale : [ [ list of present in the past (list of str) ] ,[cur] ] }

	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--eat', type=str, help='the root directory of the comf log files')
	parser.add_argument('--track', action='store_true', help='wether to repeat previous record if empty')
	parser.add_argument('--out', type=str, help='the out put directory')
	
	args = parser.parse_args()
	
	if args.track:
		track_pos = True
		
	if args.out:
		write_path = args.out
	else:
		write_path = '/client_routec'
	
	aggFolder( args.eat, write_path )
	#aggFolder( 'h3c-wx8-20161118' )

if __name__ == '__main__':
	main()
	#collect_only_mac( '1118wx/infocsv' )
'''
# Kind of deprecated, move on to the record that can keep track of time series

def extract_from_line(line : dict, all_mac_dict, cur_len=0 ,record_length = False) -> None:
	# line is the csv format line with the column are specified in all_field
	
	global enable_dis, dis_string, time_char
	
	data = line.split(',') if isinstance( line, str ) else line
	
	if data[5] == 'jn':
		try:
			all_mac_dict[ data[4] ].append( data[7] )
		except KeyError:
			if record_length:
				all_mac_dict[ data[4] ] = ([time_char]*cur_len if record_length else []) + [ data[7] ]
			else:
				all_mac_dict[ data[4] ] = [ data[7] ]
	
	elif data[5] == 'dis':
		# if enable_dis id true, then dis should be added
		# if not, dis should be emitted for ease of analysis
		if enable_dis:
			try:
				all_mac_dict[ data[4] ].append( dis_string )
			except KeyError:
				all_mac_dict[ data[4] ] = ([time_char]*cur_len if record_length else []) + [ dis_string ]
	
	elif data[5] == 'rm':
		if enable_dis:
			try:
				all_mac_dict[ data[4] ].extend( [ data[7], dis_string] )
			except KeyError:
				all_mac_dict[ data[4] ] = ([time_char]*cur_len if record_length else []) + [ data[7], dis_string ]
		else:
			try:
				all_mac_dict[ data[4] ].append( data[7] )
			except KeyError:
				all_mac_dict[ data[4] ] = ([time_char]*cur_len if record_length else []) + [ data[7] ]
	else:
		pass	
'''
