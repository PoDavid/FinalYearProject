import os
import time
import threading
import queue
import argparse

def time_change( time1, time2, absolute=False ) -> int:
	'''
	Note that number returned is time2 - time1
	'''
	if time1 == time2:
		return 0
	
	if time1 == None or time2 == None:
		return 1
	
	time1s = time1.split(' ')
	time2s = time2.split(' ')
	try:
		if time2s[2][0:2] == time1s[2][0:2] and time2s[1] == time1s[1]:
			minute = ( int(time2s[2][3:5])-int(time1s[2][3:5]) )*60
			second = ( int(time2s[2][6:8])-int(time1s[2][6:8]) )
			sum = minute + second
		else:
			sum = checktsum( time2 ) - checktsum( time1 )
	except IndexError:
		raise IndexError('Maybe you input empty string.' + str(time1) + '\n' + str(time2) )
	
	return sum if not absolute else abs(sum)

def checktsum( spot ):
	# spot can be a whole line in the log file
	if spot == None:
		return 0

	spot = spot[:20].split()

	day = int(spot[1])*86400
	hour = int(spot[2][0:2])*3600
	minute = int(spot[2][3:5])*60
	second = int(spot[2][6:8])
	
	return ( day + hour + minute + second )
	
def checktsuml_ease( spot ):
	spot = spot[:20].split()
	return  int(spot[2][3:5])*60 + int(spot[2][6:8])
	
def clean_dir( dir ):
	# make sure that the file generated different time do not conflict
	for the_file in os.listdir( dir ):
		if os.path.isfile(the_file):
			os.unlink( dir + '/' + the_file )

def check_time_order(folder_name):

	file_obj = terfread( folder_name )
	cur_time = None
	next_time = None
	
	try:
		for i in range(500):
			next_time = next(file_obj)[0]
			if time_change( cur_time, next_time ) < 0:
				raise Exception( 'Problem with time serie order!' )
	except StopIteration:
		pass
	finally:
		del file_obj
		print('time series right')
		return 0

def timin( t_list ):
	'''
	According the profiling result, this function and the checktsuml_ease it calls 
	consume most of the CPU time. It is the main reason that calling the oricomb is a CPU
	bound task. Have to work out a way to more effificiently compare the time between each
	files.
	'''
	smst = 0
	jetzt = -1
	for i in t_list:
		jetzt += 1
		if i[:20] != t_list[smst][:20] and checktsum( i ) < checktsum( t_list[smst] ):
			smst = jetzt

	return smst
		
def oricomb( path, to_path='comf', max_line=3e5 , extension='.log', bufsize=1000, wr=True ):
	'''
	this  function is for combining the orilog log files into a single series of log files, 
	then use the terfread and terfwrtie interface to play with log files.
	'''
	if not os.path.isdir( path + '/orilog' ):
		raise FileNotFoundError( 'folder path name not found' )
	else:
		clean_dir( path + '/orilog' )
				
	to_path = path + '/' + to_path
	path = path + '/orilog'
	
	if not os.path.isdir( to_path ):
		os.mkdir( to_path )
		
	if not extension.startswith('.'):
		extension = '.' + extension

	# get the file generators in the path, then get the first line of each files
	files = [ open(path + '/' + i, 'rb') for i in os.listdir(path) if i.endswith(extension) ]
	lines = [ next(i) for i in files ]
	
	print( 'num of files : ' + str(len(files)) )
	
	line_count = 0
	file_count = 0
	
	with terfwrite( to_path, extension, max_line, max_bufline=bufsize, input_encode=False ) as file_obj:
	
		# timing
		CPU_time = 0
		WRITE_time = 0
		t_s = 0
		t_s_2 = 0

		while True:
			'''
			ear_line = min( lines, key=checktsuml_ease ) # real bottleneck for cpu
			inx = lines.index(ear_line)
			'''
			t_s = time.time()

			inx = timin(lines) # real bottleneck for cpu
			ear_line = lines[inx]
			
			# timing
			t_s_2 = time.time()
			CPU_time += t_s_2 - t_s
			
			file_obj.write(ear_line)
			
			# timing
			t_s = time.time()
			WRITE_time += t_s - t_s_2
			
			try:
				lines[ inx ] = next( files[ inx ] )
			except StopIteration:
				files[inx].close()
				lines.pop(inx)
				files.pop(inx)
				if not files:
					break

			if CPU_time > 20:
				print('CPU time: '+str(CPU_time))
				print('Write time: '+str(WRITE_time))
				CPU_time = 0
				WRITE_time = 0

class terfwrite():
	def __init__(self, to_path, extension='.log', max_line=1e5, max_bufline=1000, input_encode=True):
		'''
		to_path :	isdirectly the path to write the lines into, usually looks like 'root_dir/something'
		extension :	is the file extension to add to the log files
		max_line :	the number of lines in each file, if max_line can not be devided by max_bufline,
					then actual max_line would be the minimal number that's devidable by max_bufline and 
					greater then max_line
		'''
		
		if not os.path.isdir(to_path):
			os.makedirs(to_path)
		
		self.to_path = to_path
		self.extension = extension
		self.max_line = max_line
		self.max_bufline = max_bufline
		self.input_encode = input_encode
		self.file_count = 0
		self.line_count = 0
		self.buf_count = 0
		self.bufstring_arr = []
		self.file_obj = open( self.to_path + '/' + str(self.file_count) + self.extension, 'wb' )
		self.bufques = [ queue.Queue() ]
		self.thread_pool = []
		self.thread_pool.append( threading.Thread( target = self.writhread, args=( self.bufques[-1], self.file_obj ) ) )
		self.thread_pool[-1].start()
		
	def write(self, line):
		line = line.encode() if self.input_encode else line
		self.bufstring_arr.append( line )
		self.buf_count += 1
		self.line_count += 1
		
		if self.buf_count >= self.max_bufline:
			self.bufques[-1].put( b''.join(self.bufstring_arr) )
			self.bufstring_arr = []
			self.buf_count = 0
			
			if self.line_count >= self.max_line:
				self.file_count += 1
				self.line_count = 0
				
				# signal the current file to close
				self.bufques[-1].put( False )
				
				print('entering new files : ' + str(self.file_count))
				self.file_obj = open( self.to_path + '/' + str(self.file_count) + self.extension, 'wb' )
				self.bufques.append( queue.Queue() )
				self.thread_pool.append( threading.Thread( target = self.writhread, args=( self.bufques[-1], self.file_obj ) ) )
				self.thread_pool[-1].start()
				
	def finish(self):
		# important!
		# remember to call this
		
		print('warning: function finish() is deprecated, please use content manager and with statement instead.')
		
		self.bufques[-1].put( b''.join(self.bufstring_arr) )
		self.bufques[-1].put( False )

	def writhread(self, q, fileo):
		while True:
			s = q.get(block=True, timeout=None)
			# if s is False, means to close the current file, otherwise s should be a non empty string
			if s:
				fileo.write( s )
			else:
				break

		fileo.close()

	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
	
		if exc_type is not None:
			print(exc_type, exc_value, traceback)
			raise exc_type
			
		self.bufques[-1].put( b''.join(self.bufstring_arr) )
		self.bufques[-1].put( False )
		
class terfread():
	'''
	terfread should be called to read folder created by terfwrite and oricomb
	use it as a generator
	'''
	def __init__(self, path, extension='.log', output_decode=True, max_iter=-1 ):
		self.path = path
		self.file_obj = None
		self.extension = extension if extension.startswith('.') else ('.'+extension)
		
		# to track with log file has been open right now
		self.file_inx = 0
		self.output_decode = output_decode
		
		# to track the iteration
		self.max_iter = max_iter
		self.iter = 0
		
		self.force_stop = False

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		return exc_type is Exception
		
	def __iter__(self):
		self.file_obj = open(self.path + '/' + str(self.file_inx) + self.extension, 'rb' )
		return self
		
	def __next__(self):
		if self.file_obj:
			try:
				line = next(self.file_obj)
				if line:
					# check if the reading amount is all done
					if (self.max_iter is not -1) and self.iter >= self.max_iter:
						self.force_stop = True
						raise StopIteration
					else:
						self.iter += 1
						if self.output_decode:
							# let outer function to handle the unicode decode error
							try:
								decoded_line = line.decode('utf-8')
							except UnicodeDecodeError as err:
								# handle the error internally
								decoded_line = 'UnicodeDecodeError => ' + str(err)
							return decoded_line
						else:
							return line
				else:
					raise TypeError('terfread getting none result')

			except StopIteration:
				self.file_obj.close()
				
				if self.force_stop:
					raise StopIteration
				else:
					self.file_inx += 1

		try:
			print('read into next file')
			self.file_obj = open(self.path + '/' + str(self.file_inx) + self.extension, 'rb' )
			if self.output_decode:
				# let outer function to handle the unicode decode error
				return next(self.file_obj).decode('utf-8')
			else:
				return next(self.file_obj)
				
		except FileNotFoundError:
			print('leaving generator')
			raise StopIteration
	
def main():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--eat', type=str, help='the root directory of the ori log files')
	
	args = parser.parse_args()

	oricomb( args.eat )

if __name__ == '__main__':
	main()
