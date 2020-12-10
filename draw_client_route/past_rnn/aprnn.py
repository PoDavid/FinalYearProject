import numpy as np
import lasagne
import neto
import pairt

import theano
import theano.tensor as T

################################
# theano variable

x = T.ftensor3('x')
y = T.ftensor3('y')
apid_num = 1000
info_for_ap = 4
time_len = 10
n_epoch = 2
batch_size = 50
cut_size = 50
learning_rate = 1
test_len = 1000

loss_record_file = 'aprnn_long_loss.txt'
test_record_file = 'test_result.txt'

################################

'''
Explaination:

in the AP_onehot1118f.npy file, the data is stored as a array with shape ( 17280, 4000 )
17280 is the number of the period in a day (each period is 5 seconds long)
4000 is the information for each period ( 1000 APID * 4 info for each APID ), 4 info are specified in the setdata.py
I call these 4000 period dots

then I cut the data into 10 dots per pieces. which is like [0,1,2...8,9], [1,2,3...9,10] ,[2,3,4...,10,11]
and each series are paired with next dot then are put togother into the neural networks to train

'''

def build_lstm():
	global apid_num, time_len
	l_inp = lasagne.layers.InputLayer( (1, None, apid_num*info_for_ap), input_var=x )
	l_lstm = lasagne.layers.LSTMLayer(l_inp, num_units=apid_num*info_for_ap)
	return l_lstm

def compile_tfunc(network):
	global learning_rate
	
	# here we extract the last element of the sequence output
	all_result = lasagne.layers.get_output(network)
	#last_result = all_result[-1]
	#last_result, _ = theano.scan(lambda xi: xi[-1], sequences = [all_result] )
	
	loss_ori = lasagne.objectives.squared_error(all_result, y)
	loss = loss_ori.sum()

	params_lstm = lasagne.layers.get_all_params(network, trainable=True)
	updates_lstm  = lasagne.updates.nesterov_momentum( loss, params_lstm, learning_rate = learning_rate, momentum=0.9 )
	
	'''
	# The following is almost equivalent code for lasagne.updates.nesterov_momentum
	# Only that it does not use the momentum
	# Just left here for the ease of future debgging
	
	from collections import OrderedDict
	
	grads = T.grad(loss, params_lstm)
	updates_lstm = OrderedDict()
	
	for param, grad in zip(params_lstm, grads):
		updates_lstm[param] = param - grad*learning_rate
	'''
	
	train_lstm = theano.function( [x, y], loss, updates = updates_lstm )
	test_lstm = theano.function( [x], all_result )
	
	return train_lstm, test_lstm

def parepare_fse_data(train_input, train_target, re_list):
	
	global cut_size, batch_size
	
	inp = []
	tar = []
	
	randseries = np.random.random_integers( 0, len(train_input) -cut_size -1 , batch_size )
	
	for inx in randseries:
		
		inp.append( train_input[ inx:(inx+cut_size) ] )
		tar.append( train_input[ inx:(inx+cut_size) ] )

	re_list[0] = inp
	re_list[1] = tar
	re_list[2] += 1
	
def main_train_v2( train_fn, train_input, train_target ):

	global n_epoch, batch_size, cut_size
	
	import threading
	
	trlen = len(train_input)
	
	# since here we use the whole series to train
	# assert train_input.shape == train_target.shape

	spot_num = apid_num*info_for_ap
	
	next_data_package = [ 0, 0, -1 ]
	curr_data_package = [ 0, 0, -1 ]
	
	# we hope to modify next_data_package in another thread, hence I do it in the form of list
	# after this line, next_data_package would contain the data we put into the theano function
	parepare_fse_data(train_input, train_target, next_data_package)

	with open(loss_record_file, 'a') as infile:

		for cur_epoch in range(n_epoch):
			temp_loss = 0
			loss = 0

			curr_data_package = next_data_package
			
			packing_thread = threading.Thread( target=parepare_fse_data, args=( train_input, train_target, next_data_package ) )
			packing_thread.start()

			# make sure we susccessfully update the data package
			assert curr_data_package[2] == cur_epoch
			
			loss = train_fn( curr_data_package[0], curr_data_package[1] )
			
			packing_thread.join()
			
			mean_loss = loss / (spot_num)

			re_string = 'epoch ' + str(cur_epoch) + ' : ' + str(mean_loss) + '\n'
			print( re_string )
			infile.write( re_string ) 

def test(test_fn, test_input, test_target):
	'''
	So far I havn't figure out a way to evaluate the accuracy, maybe the only thing reliable now is the loss
	'''
	
	all_res = test_fn( test_input )
	
	pairt.tiffer( test_target, all_res, plot_sample=1, filename=test_record_file )
	
	np.save('target', test_target)
	np.save('result', all_res)

def main():
	global apid_num, test_len
	
	filename = 'AP_onehot1118f.npy'
	re_filename = 'firnn'
	
	trained_path = 'aprnn_t'
	
	print('loading data from ' + filename)
	
	maindata = np.load(filename)
	data_len = len(maindata)
	
	print('building network')
	network = build_lstm()
	
	train_fn, test_fn = neto.get_result_tofola(trained_path, network, compile_tfunc)
	
	train_input, train_target = [], []
	test_input, test_target = [], []
	
	# Here we get the starting point of the testor, 
	# then we put the series before the ques and after the ques+test_len into training
	# we limit the random range when choosing the ques lest the the series after ques+test_len is too small, making the training meaningless
	ques = np.random.randint(0, (data_len-test_len * 2) )
	
	print('preparing data')
	print( 'data len :  ' + str(data_len) )
	# prepare the training and testing data
	cur_pos = 0
	
	'''
	# deprecated
	# prepare the data
	while cur_pos < data_len-time_len-1:
		if cur_pos in ques:
			test_input.append( maindata[ cur_pos:(cur_pos+time_len) ] )
			test_target.append( maindata[ (cur_pos+time_len) ] )
		else:
			train_input.append( maindata[ cur_pos:(cur_pos+time_len) ] )
			train_target.append( maindata[ (cur_pos+time_len) ] )
		cur_pos += 1
	'''
	
	# prepare the data
	# this should be the desired way to test, but it's troublesome, so I don't do testing for now
	'''
	test_input.append( maindata[ ques : (ques+test_len) ] )		
	test_target.append( maindata[ ques+1 : (ques+test_len+1) ] )		

	train_input.append( maindata[ 0 : ques ] )
	train_target.append( maindata[ 1 : (ques+1) ] )

	train_input.append( maindata[ (ques+test_len) : -1 ] )
	train_target.append( maindata[ (ques+test_len+1) : ] )
	
	train_input, train_target = np.array(train_input), np.array(train_target)
	test_input, test_target = np.array(test_input), np.array(test_target)
	'''
	train_input = maindata[ 0:-1 ]
	train_target = maindata[ 1: ]
	

	for nepo in range(1):
		print( 'Big training cycle : ' + str(nepo) )
	
		print('start training ')
		main_train_v2( train_fn, train_input, train_target )
		print('training finish')

		#testing, need to be enhanced
		#test(test_fn, test_input, test_target)

		neto.store_result_tofola( trained_path, network, [ train_fn, test_fn ], [loss_record_file, test_record_file] )
		
		'''
		# replaced by the great function store_result_tofola
		neto.store_network( network, 'aprnnl/'+re_filename+str(nepo)+'.net' )
		
		# sometimes may raise recursion exception
		neto.store_compiled_fn( (train_fn, test_fn), 'aprnnl/'+re_filename+str(nepo)+'.pic' )
		'''
if __name__ == '__main__':
	main()
	
##############################################################################
'''
leaving the program without loading the following code, which are deprecated and just left for possible future traceback
'''
import sys
sys.exit(0)
	
def main_train_single_batch_v1( train_fn, train_input, train_target ):

	global n_epoch, batch_size, cut_size
	
	trlen = len(train_input)
	
	# since here we use the whole series to train
	# assert train_input.shape == train_target.shape

	spot_num = apid_num*info_for_ap
	
	with open(loss_record_file, 'a') as infile:
		for cur_epoch in range(n_epoch):
			temp_loss = 0
			loss = 0
			
			for t_inp, t_tar in zip( train_input, train_target ):
			
				# since the whole series is too long, and will lead to exploding gradient,
				# Hence I still do it on batch, delibrately seperate the huge series
				
				lent_inp =  len( t_inp )
				cur_b = 0
				
				while cur_b  < ( lent_inp-1 ) :

					endp = cur_b + cut_size if cur_b + cut_size < len( t_inp ) else lent_inp

					temp_loss = train_fn( [t_inp[cur_b:endp]] , [t_tar[cur_b:endp]] )
					loss += temp_loss / cut_size
					infile.write(' loss : ' + str(loss) + ' single_loss : ' + str(temp_loss) + '\n') 

					cur_b += int( cut_size/2 )

			mean_loss = loss / (spot_num)

			re_string = 'epoch ' + str(cur_epoch) + ' : ' + str(mean_loss) + '\n'
			print( re_string )
			infile.write( re_string ) 
			
			
def main_train_v0( train_fn, train_input, train_target ):
	
	# deprecated , this is for only let a seire of ten unit to predict the eleventh unit

	global n_epoch, batch_size
	
	# for shuffling later
	combarr = [ (i, j) for i, j in zip(train_input, train_target) ]
	
	trlen = len(combarr)
	batch_num = trlen/batch_size
	spot_num = apid_num*info_for_ap
	
	with open(loss_record_file, 'a') as infile:
		for i in range(n_epoch):
			
			# make sure that each epoch we get different training order
			# cur_b record the current batch number
			np.random.shuffle(combarr)
			loss = 0
			cur_b = 0

			while cur_b+batch_size < trlen:
				
				t_input = [ i[0] for i in combarr[cur_b:cur_b+batch_size] ]
				t_target = [ i[1] for i in combarr[cur_b:cur_b+batch_size] ]

				# temp_loss represent the loss for each time serie
				# loss is used to calculate the average loss for each serie
				temp_loss = train_fn( t_input, t_target ) / spot_num
				loss += temp_loss
				infile.write('batch : ' + str(cur_b) + ' loss : ' + str(loss) + ' single_loss : ' + str(temp_loss) + '\n') 
				cur_b += batch_size

			if cur_b+batch_size != trlen - 1:
				t_input = [ i[0] for i in combarr[cur_b:] ]
				t_target = [ i[1] for i in combarr[cur_b:] ]
				
				temp_loss = train_fn( t_input, t_target ) / spot_num
				loss += temp_loss
				infile.write('batch : ' + str(cur_b) + ' loss : ' + str(loss) + ' single_loss : ' + str(temp_loss) + '\n' ) 
			
			re_string = 'epoch ' + str(i) + ' : ' + str(loss*spot_num/trlen) + '\n'
			print( re_string )
			infile.write( re_string ) 
	
	