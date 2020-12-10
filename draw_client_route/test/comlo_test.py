import comlo
import unittest
import cProfile

class TestComlo(unittest.TestCase):
	def test_checktsuml_test(self):
		spots = [
			'Nov 18 00:00:00 2016 info 147.8.123.17 HKU-H3C-WX6103-7 -Use',
			'Nov 18 00:00:05 2016 info afdijslfkjs HKU-H3C-WX6103-7 -Use',
			'Nov 18 05:40:56 2016 info 147.8.123.17 H3C WX6103-8 info',
			'Nov 18 00:00:32 2016 info 147.8.123.17 HKU-H3C-WX6103-8 info',
			'Nov 18 00:06:12 2016 info 147.8.123.17 H3C WX6103-8 info',
			'Nov 18 03:16:27 2016 info 147.8.123.17 H3C WX6103-8 info'
		]

		ans = [ 0, 5, 2456, 32, 372, 987 ]
		
		for i,j in zip(spots, ans):
			self.assertEqual( comlo.checktsuml_ease(i) , j )
			
		inx = spots.index( max(spots, key=comlo.checktsuml_ease) )
		
		self.assertEqual( inx, 2 )
	
	def test_oricomb_1(self):
		try:
			comlo.oricomb( 'testcomlo', max_line=50, bufsize=30 )
		except FileNotFoundError as err:
			raise FileNotFoundError( str(err)  + '\nOr maybe you did not get the testcomlo folder?' )
			
		self.assertTrue( True )
		
	def test_terfread(self):
		fr = comlo.terfread('testcomlo/comf')
		
		with comlo.terfwrite('testcomlo/comtest') as fw:
			for i in fr:
				fw.write(i)
	
	def test_time_change_1(self):
		time1 = '11 18 00:00:35 2016'
		time2 = '11 18 00:00:36 2016'
		time3 = '11 18 00:00:38 2016'
		time4 = '11 18 00:01:38 2016'
		
		self.assertEqual( comlo.time_change(time1, time2), 1 )
		self.assertEqual( comlo.time_change(time2, time3), 2 )
		self.assertEqual( comlo.time_change(time3, time4), 60 )
		self.assertEqual( comlo.time_change(time1, time4), 63 )
		
def cpro_oricomb():
	cProfile.run( 'comlo.oricomb( "testcomlo", max_line=50, bufsize=30 )' )
	
def main():
	unittest.main()
		
if __name__ == '__main__':
	main()