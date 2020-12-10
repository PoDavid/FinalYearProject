import unittest
import aggClient

class TestAggClient_ext(unittest.TestCase):
	def test_extract_from_line_2(self):
		cur_len = 3
		handled_mac_set = { '0cd7-461d-e931', '5844-9821-f3ad', '7048-0f75-fbd6' }
		all_mac_dict = {}
		
		the_string = 'Jun 6 11:49:33 2016,info,147.8.123.17,HKU-H3C-WX6103-7,0cd7-461d-e931,rm,,237,70ba-efca-1962,,110,0023-896a-b2c2,127.0.0.1,127.0.0.1.,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		the_string = 'Jun 6 11:49:33 2016,info,147.8.123.17,HKU-H3C-WX6103-7,0cd7-461d-e931,rm,,110,70ba-efca-1962,,238,0023-896a-b2c2,127.0.0.1,127.0.0.1.,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		the_string = 'Jun 6 11:49:33 2016,info,147.8.123.17,HKU-H3C-WX6103-7,0cd7-461d-e931,rm,,238,70ba-efca-1962,,239,0023-896a-b2c2,127.0.0.1,127.0.0.1.,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		the_string = '11 18 00:00:01 2016,info,147.8.123.17,HKU-H3C-WX6103-7,5844-9821-f3ad,dis,HKU,,,65534,,,,,,,,,,,,,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		the_string = '11 18 00:00:15 2016,info,147.8.123.17,HKU-H3C-WX6103-7,7048-0f75-fbd6,jn,eduroam,234,70ba-efc9-fbc1,,,,,,,,,,,,,,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		the_string = '11 18 00:00:32 2016,info,147.8.123.17,HKU-H3C-WX6103-7,8429-9969-11b5,jn,eduroam,232,0023-895d-a1a1,,,,,,,,,,,,,,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )
		
		e = aggClient.enable_dis
		if e:
			self.assertEqual( all_mac_dict[ '0cd7-461d-e931' ], [ [ ',,,' ], ['237', 'dis', '110', 'dis', '238', 'dis'] ] )
			self.assertEqual( all_mac_dict[ '5844-9821-f3ad' ], [ [ ',,,' ], ['dis'] ] )
			self.assertEqual( all_mac_dict[ '7048-0f75-fbd6' ], [ [ ',,,' ], ['234'] ] )
		else:
			self.assertEqual( all_mac_dict[ '0cd7-461d-e931' ], [ [ ',,,' ], ['237', '110', '238'] ] )
			self.assertEqual( all_mac_dict[ '5844-9821-f3ad' ], [ [ ',,,' ], [] ] )
			self.assertEqual( all_mac_dict[ '7048-0f75-fbd6' ], [ [ ',,,' ], ['234'] ] )
			
		aggClient.time_pass(all_mac_dict)
		
		if e:
			self.assertEqual( all_mac_dict[ '0cd7-461d-e931' ], [ [ ',,,', '237-dis-110-dis-238-dis' ], [] ] )
			self.assertEqual( all_mac_dict[ '5844-9821-f3ad' ], [ [ ',,,', 'dis' ], [] ] )
			self.assertEqual( all_mac_dict[ '7048-0f75-fbd6' ], [ [ ',,,', '234' ], [] ] )
		
		aggClient.time_pass(all_mac_dict)
		
		if e:
			self.assertEqual( all_mac_dict[ '0cd7-461d-e931' ], [ [ ',,,', '237-dis-110-dis-238-dis', '' ], [] ] )
			self.assertEqual( all_mac_dict[ '5844-9821-f3ad' ], [ [ ',,,', 'dis', '' ], [] ] )
			self.assertEqual( all_mac_dict[ '7048-0f75-fbd6' ], [ [ ',,,', '234', '234' ], [] ] )
			
		aggClient.time_pass(all_mac_dict)
		
		if e:
			self.assertEqual( all_mac_dict[ '0cd7-461d-e931' ], [ [ ',,,', '237-dis-110-dis-238-dis', '', '' ], [] ] )
			self.assertEqual( all_mac_dict[ '5844-9821-f3ad' ], [ [ ',,,', 'dis', '', '' ], [] ] )
			self.assertEqual( all_mac_dict[ '7048-0f75-fbd6' ], [ [ ',,,', '234', '234', '234' ], [] ] )
			
		the_string = '11 18 00:00:35 2016,info,147.8.123.17,HKU-H3C-WX6103-7,dc41-5fd9-67de,rm,,603,80f6-2e53-5723,,106,0023-896a-b8e3,127.0.0.1,127.0.0.1.,,,,,,,,,,,'
		aggClient.extract_from_line_2( the_string.split(','), all_mac_dict, cur_len, handled_mac_set )

		self.assertFalse( all_mac_dict.get('dc41-5fd9-67de', False)  )
		self.assertTrue( e )
		
	def test_time_pass_1(self):
		
		mac_dict_t = { 
						'0cd7-461d-e931': [ [ ',','125-dis-123' ], [] ] 
						}
		aggClient.time_pass(mac_dict_t)
		self.assertEqual( mac_dict_t[ '0cd7-461d-e931' ][0][-2] , '125-dis-123' )
		self.assertEqual( mac_dict_t[ '0cd7-461d-e931' ][0][-1] , '123' )

def main():
	unittest.main()
		
if __name__ == '__main__':
	main()
	
	