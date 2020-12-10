import numpy as np
import lasagne
import lasagne.layers as lay
import neto
import pairt
import time

import theano
import theano.tensor as T

################################
# theano variable

x = T.ftensor3('x')
y = T.ftensor3('y')
l_rate = T.scalar('r')

################################

apid_num = 1000
info_for_ap = 4
hidden_unit = 8000
n_epoch = 200
batch_size = 200
cut_size = 20
move_size = 10
learning_rate = 0.0000005
test_len = 1000
ques = 10000

loss_record_file = 'aprden_long_loss.txt'
test_record_file = 'test_result.txt'
envr_record_file = 'envr_record.txt'

temp_loss_file = 'temp_loss.txt'

################################

'''
Explaination:

in the AP_onehot1118f.npy file, the data is stored as a array with shape ( 17280, 4000 )
17280 is the number of the period in a day (each period is 5 seconds long)
4000 is the information for each period ( 1000 APID * 4 info for each APID ), 4 info are specified in the setdata.py
I call these 4000 period dots

'''

def build_lstm():
	global apid_num, info_for_ap, hidden_unit
	input_len = apid_num*info_for_ap
	
	l_inp = lay.InputLayer( (None , None, input_len), input_var=x )
	
	# get the real shape that is declare as (None, None, input_len)
	batchsize, serie_len, _ = l_inp.input_var.shape
	middle_len = 2000
	
	h_layer = lay.ReshapeLayer(l_inp, (-1, input_len))
	h_layer = lay.DenseLayer(h_layer, num_units=middle_len)
	h_layer = lay.ReshapeLayer(h_layer, (batchsize, serie_len, middle_len))

	h_layer = lay.LSTMLayer(h_layer, num_units=2000)
	
	h_layer = lay.ReshapeLayer(h_layer, (-1, 2000))
	h_layer = lay.DenseLayer(h_layer, num_units=input_len)
	h_layer = lay.ReshapeLayer(h_layer, (batchsize, serie_len, input_len))

	return h_layer

def compile_tfunc(network):
	global l_rate
	
	# here we extract the last element of the sequence output
	all_result = lasagne.layers.get_output(network)
	#last_result = all_result[-1]
	#last_result, _ = theano.scan(lambda xi: xi[-1], sequences = [all_result] )
	
	loss_ori = lasagne.objectives.squared_error(all_result, y)
	loss = loss_ori.sum()

	params_lstm = lasagne.layers.get_all_params(network, trainable=True)
	updates_lstm  = lasagne.updates.nesterov_momentum( loss, params_lstm, learning_rate = l_rate, momentum=0.9 )
	
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
	
	train_lstm = theano.function( [x, y, l_rate], loss, updates = updates_lstm )
	test_lstm = theano.function( [x], all_result )
	
	return train_lstm, test_lstm
	
def main_train( train_fn, train_input, train_target ):

	global n_epoch, batch_size, cut_size, learning_rate

	# for shuffling later
	combarr = [ (i, j) for i, j in zip(train_input, train_target) ]
	
	trlen = len(train_input)
	batch_num = int( trlen/batch_size )
	spot_num = apid_num*info_for_ap
	
	print( 'training len : ' + str( trlen ) )
	
	with open(temp_loss_file, 'w') as infile:
		for cur_epoch in range(n_epoch):
		
			# make sure that each epoch we get different training order
			# cur_b record the current batch number
			np.random.shuffle(combarr)
			loss = 0
			cur_b = 0

			while cur_b+batch_size < trlen:
			
				# may be not efficient, can open a new thread doing this
				t_input = np.array( [ i[0] for i in combarr[cur_b:cur_b+batch_size] ] )
				t_target = np.array( [ i[1] for i in combarr[cur_b:cur_b+batch_size] ] )

				assert t_input.dtype == np.int8

				# temp_loss represent the loss for each time serie
				# loss is used to calculate the average loss for each serie
				temp_loss = train_fn( t_input, t_target, learning_rate ) / spot_num
				loss += temp_loss
				infile.write('batch : ' + str(cur_b) + ' loss : ' + str(loss) + ' single_loss : ' + str(temp_loss) + '\n') 
				cur_b += batch_size
			
			# deal with the last batch, which th elength would be different from above
			if cur_b+batch_size != trlen - 1:
				t_input = [ i[0] for i in combarr[cur_b:] ]
				t_target = [ i[1] for i in combarr[cur_b:] ]
				
				temp_loss = train_fn( t_input, t_target, learning_rate  ) / spot_num
				loss += temp_loss
				infile.write('batch : ' + str(cur_b) + ' loss : ' + str(loss) + ' single_loss : ' + str(temp_loss) + '\n' ) 
			
			re_string = 'learning rate : ' + str(learning_rate) + '\n' + 'epoch ' + str(cur_epoch) + ' : ' + str(loss/trlen) + '\n'
			print( re_string )
			infile.write( re_string )
			
			if np.isnan(loss):
				print( 'NAN problem!!' )
				raise Exception

	with open( temp_loss_file, 'r' ) as ftemp, open( loss_record_file, 'a' ) as floss:
		floss.write( ftemp.read() )

def test(test_fn, test_input, test_target):
	'''
	So far I havn't figure out a way to evaluate the accuracy, maybe the only thing reliable now is the loss
	'''
	
	all_res = np.around( test_fn( test_input ) ).astype('i')

	pairt.tiffer( np.array( test_target[0] ), np.array( all_res[0] ), plot_sample=3, filename=test_record_file )

def test_trainingdata( test_fn, test_input, test_target ):
	
	all_res = test_fn( test_input )
	pairt.tiffer( np.array( test_target[0] ), np.array( all_res[0] ), plot_sample=3, filename=train_record_file )
	
def prepare_data( maindata, train_input, train_target, test_input, test_target ):
	
	global test_len, ques
	
	# Here we get the starting point of the testor, 
	# then we put the series before the ques and after the ques+test_len into training
	# we limit the random range when choosing the ques lest the the series after ques+test_len is too small, making the training meaningless
	ques = np.random.randint(0, (len(maindata-test_len * 2) ) ) if ques == None else ques
	print( 'ques = ' + str(ques) )

	# prepare the training and testing data
	cur_pos = 0
	
	cut_tail = True
	
	# data before test cases
	while cur_pos + cut_size + 1 < ques:	
		train_input.append( maindata[ cur_pos: (cur_pos+cut_size) ] )
		train_target.append( maindata[ cur_pos+1 : (cur_pos+cut_size+1) ] )
		cur_pos += move_size
	
	if not cut_tail:
		train_input.append( maindata[ cur_pos: ques-1 ] )
		train_target.append( maindata[ cur_pos+1 : ques ] )

	# prepare the test cases
	test_input.append( maindata[ cur_pos: cur_pos+test_len-1 ] )
	test_target.append( maindata[ cur_pos+1 : cur_pos+test_len ] )

	# prepare the test cases
	cur_pos = cur_pos + test_len
	while cur_pos + cut_size < len(maindata):
		train_input.append( maindata[ cur_pos: (cur_pos+cut_size) ] )
		train_target.append( maindata[ cur_pos+1 : (cur_pos+cut_size+1) ] )
		cur_pos += move_size

	if not cut_tail:
		train_input.append( maindata[ cur_pos: -1 ] )
		train_target.append( maindata[ cur_pos+1 : ] )
	
def main():
	global apid_num, test_len, cut_size, move_size
	
	filename = 'AP_onehot1118f.npy'
	trained_path = 'aprden2_t'
	
	print('loading data from ' + filename)
	maindata = np.load(filename)
	
	print('building network')
	network = build_lstm()
	
	train_fn, test_fn = neto.get_result_tofola(trained_path, network, compile_tfunc)

	# prepare the data
	train_input, train_target = [], []
	test_input, test_target = [], []
	
	print('preparing data')
	print( 'data len :  ' + str( len(maindata) ) )
	
	prepare_data( maindata, train_input, train_target, test_input, test_target )

	for nepo in range(6):
		print( 'Big training cycle : ' + str(nepo) )
	
		print('start training ')
		main_train( train_fn, train_input, train_target )
		print('training finish')

		# no matter what happen in the test, we still have to store the result and the compiled function
		try:
			#testing, need to be enhanced
			test(test_fn, test_input, test_target)
		
		finally:
			neto.store_result_tofola( trained_path, network, [ train_fn, test_fn ], [loss_record_file, test_record_file] )

if __name__ == '__main__':
	main()
