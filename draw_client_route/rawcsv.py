import os
import comlo
import argparse

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

month_table = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
	
class NotCategorizedError(Exception):
	'''
	For lines that are not categorized yet, detect it and throw this exception
	'''
	pass
	
def row_info( line_d ) -> list:
	assert isinstance(line_d, list)
	tempd = [''] * len(all_field)
	# compress the month name to a number
	tempd[ 0 ] = ' '.join( [ str(month_table.index( line_d[ 0 ] ) + 1 ).zfill(2) ] + line_d[ 1:4 ])
	tempd[ 1 ] = 'info'
	
	if line_d[7] == 'Client':
		tempd[ 2 ], tempd[ 3 ], tempd[ 4 ] = ( line_d[5], line_d[6], line_d[8] )
		if line_d[9] == 'successfully':
			# hope to record the joins activity, instead of just success
			tempd[ 5 ] = 'jn'
			# for getting the wifi name, we have to join them and split it again
			line_d = ' '.join(line_d[12:]).split(', on ')
			tempd[ 6 ], line_d = ( line_d[0].strip(','), line_d[1].split(' ') )
			
			tempd[ 7 ] = line_d[1]
			tempd[ 8 ] = line_d[4].strip('.')
		elif line_d[9] == 'disconnected':
			tempd[ 5 ] = 'dis'
			# for getting the wifi name, we have to join them and split it again
			line_d = ' '.join(line_d[12:]).split('. Reason ')
			tempd[ 6 ] = line_d[0]
			line_d = line_d[1].split(' ')
			tempd[ 9 ] = line_d[2].strip('.')
		elif line_d[9] == 'roamed':
			tempd[ 5 ] = 'rm'
			line_d = ' '.join(line_d[12:]).split(' ')
			# entering AP information
			tempd[ 7 ], tempd[ 8 ], tempd[ 13 ] = line_d[9], line_d[12], line_d[15]
			# leaving AP information
			tempd[ 10 ], tempd[ 11 ], tempd[ 12 ] = (line_d[0], line_d[3], line_d[6])
		else:
			print('empty info line')
			
	elif line_d[7] == 'Synchronizing':
		# assign all sort of things, see all_field for secifying
		tempd[ 2 ], tempd[ 3 ], tempd[5], tempd[ 7 ], tempd[ 14 ], tempd[ 15 ], tempd[ 16 ] = \
			( line_d[5], line_d[6], 'bk', line_d[ 12 ], line_d[ 14 ].strip(','), line_d[ 18 ], line_d[ 21 ].strip('.') )
	elif line_d[7] == 'Channel':
		tempd[ 2 ], tempd[ 3 ], tempd[5], tempd[ 7 ], tempd[ 14 ], tempd[ 15 ], tempd[ 16 ] = \
			( line_d[5], line_d[6], 'ch', line_d[11].strip(','), line_d[13], line_d[16], line_d[19].strip('.') )
	elif line_d[7] == 'Radar':
		return False
	elif line_d[7].startswith('-'):
		return False
		'''
		# do not delete this
		if line_d[-1] == 'successfully' and line_d[-2] == 'online':
			pass
		elif line_d[-1] == 'authentication' and line_d[-2] == '802.1X':
			pass
		elif line_d[-1] == 'off' and line_d[-2] == 'logged':
			pass
		elif line_d[-1] == 'terminated' and line_d[-2] == 'was':
			pass
		else:
			print( line_d )
			print( line_d[7] )
			#time.sleep(3)
			print('unidentified info dash line')
		'''
	elif line_d[7].startswith('Trap'):
		return False
	else:
		print('unidentified info line')
		print( line_d )
		print( line_d[7] )
		return False
	return tempd
	
def row_warning( line_d ) -> list:
	assert isinstance(line_d, list)
	tempd = [''] * len(all_field)
	# compress the month name to a number
	tempd[ 0 ] = ' '.join( [ str(month_table.index( line_d[ 0 ] ) + 1 ) ] + line_d[ 1:4 ])
	tempd[ 1 ] = 'warn'
	tempd[ 2 ], tempd[ 3 ] = ( line_d[5], line_d[6] )
	
	if len( line_d ) <= 8:
		pass
	elif line_d[8] == 'interfere(t):':
		if line_d[9] == 'AP':
			tempd[ 17 ] = 'AP itf'
			tempd[ 20 ] = line_d[20][6:]
		elif line_d[9] == 'Channel':
			tempd[ 17 ] = 'chl itf'
		else:
			raise NotCategorizedError
			
		tempd[ 18 ], tempd[ 19 ], tempd[ 14 ], tempd[ 15 ]  = \
			( line_d[12][1:], line_d[15][3:], line_d[17][3:], line_d[19][7:] )
		
		
	elif line_d[8] == 'interfere':
		tempd[ 17 ] = 'STA itf'
		tempd[ 18 ] = line_d[13][1:]
		tempd[ 19 ] = line_d[16][3:]
		tempd[ 14 ] = line_d[18][3:]
		tempd[ 15 ] = line_d[20][7:]
		tempd[ 21 ] = line_d[21][7:]
		
	elif line_d[7] == 'Disconnect(t):':
		'''
		Not Finished Yet. this part is too hard and too many new field would take a lot of space.
		'''
		pass
		if line_d[8] == 'Station':
			# line_d[9] would be like 'Disconnect:1.3.6.1.4.1.25506.2.75.3.2.0.8<hh3cDot11StationDisconnectTrap>'
			tempd[18] = line_d[9].split(':')[1]
			tempd[21] = line_d[10].split(':')[1]
			tempd[22] = line_d[11].split(':')[1]
			tempd[23] = line_d[13].split(':')[1]
			tempd[8] = line_d[14].split(':')[1]
		elif line_d[8] == 'User':
			tempd[18] = line_d[9].split(':')[1]
			tempd[23] = line_d[11].split(':')[1]
			tempd[21] = line_d[12].split(':')[1]
			tempd[24] = line_d[14].split(':')[1]
		else:
			raise NotCategorizedError('in Disconnect(t)')
	elif line_d[7].startswith('Disassociate'):
		pass
	elif line_d[7] == 'TRAP(t):':
		pass
	else:
		pass
		#raise NotCategorizedError( 'in warning' )
		
	return tempd
	
def read_in_order():
	with open('wifiraw_info.csv', 'w') as csvf:
		with open('h3c-wx7-20161118.log', 'r') as wifilog:
			for line in wifilog:
				after_list = False
				line_d = line.split()
				if line_d[4] == 'info':
					after_list = row_info( line_d )
				elif line_d[4] == 'warning':
					pass
				#	after_list = row_warning( line_d )
				elif line_d[4] == 'notice':
					pass
				else:
					print('unidentified line')
					print(line)
					break

				if after_list:
					csvf.write( ','.join(after_list) + '\n' )
					
def read_inr(folder_path):
	'''
	read in the log files from the interface provided by the comlo interface
	extract some of the info lines and store them into the csv files
	'''

	if not os.path.isdir(folder_path + '/infocsv'):
		os.makedirs(folder_path + '/infocsv')
	try:
		terfin = comlo.terfread( folder_path + '/comf', output_decode=False )
		
		with comlo.terfwrite( folder_path + '/infocsv' ) as terfout:
			for line in terfin:
				after_list = False
				
				# the handling was added since that there are cases some unknown names appear in the log file
				try:
					line_d = line.decode('utf-8').split()
				except:
					with open(folder_path + '/err.log', 'ab') as errfw:
						errfw.write( line )

				if line_d[4] == 'info':
					after_list = row_info( line_d )
				elif line_d[4] == 'warning':
					pass
				#	after_list = row_warning( line_d )
				elif line_d[4] == 'notice':
					pass
				else:
					print('unidentified line')
					print(line)
					break

				if after_list:
					terfout.write( ','.join(after_list) + '\n' )
			
	except NotCategorizedError as err:
		print(err)
		print(line)
	
	except Exception as err:
		print(type(err))
		print(err)
		print(line)
		print(len(line_d))
		import sys, traceback
		traceback.print_exc(sys.exc_info()[2], file=sys.stdout)
			
def main():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--eat', type=str, help='the root directory of the comf log files')
	
	args = parser.parse_args()
	
	read_inr( args.eat )
	#read_inr('h3c-wx8-20161118.log')

if __name__ == '__main__':
	main()