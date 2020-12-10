import rawcsv
import aggClient
import unittest

class TestRawcsv_info(unittest.TestCase):

	def test_row_info_sus_1(self):
		the_string = 'Jun  6 11:53:02 2016 info 147.8.123.18 HKU-H3C-WX6103-8  Client 3ca9-f481-5e60 successfully joins WLAN HKU, on APID 468 with BSSID 0023-895d-a3a3.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[0], '06 6 11:53:02 2016' )
		self.assertEqual( arr[1], 'info' )
		self.assertEqual( arr[2], '147.8.123.18' )
		self.assertEqual( arr[7], '468' )
		self.assertEqual( arr[8], '0023-895d-a3a3' )
		
	def test_row_info_sus_2(self):
		the_string = 'Jun  6 11:53:00 2016 info 147.8.123.18 HKU-H3C-WX6103-8  Client f81a-671c-df1a successfully joins WLAN Universities WiFi, on APID 169 with BSSID 3822-d61f-1470.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[3], 'HKU-H3C-WX6103-8' )
		self.assertEqual( arr[4], 'f81a-671c-df1a' )
		self.assertEqual( arr[6], 'Universities WiFi' )
		self.assertEqual( arr[7], '169' )

	def test_row_info_sus_3(self):
		the_string = 'Jun  6 11:53:01 2016 info 147.8.123.18 HKU-H3C-WX6103-8  Client 4400-109e-d2ea successfully joins WLAN eduroam, on APID 440 with BSSID 5866-baa0-9fc1.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[1], 'info' )
		self.assertEqual( arr[5], 'jn' )
		self.assertEqual( arr[6], 'eduroam' )
		self.assertEqual( arr[8], '5866-baa0-9fc1' )
		
	def test_row_info_dis_1(self):
		the_string = 'Jun  6 11:53:00 2016 info 147.8.123.18 HKU-H3C-WX6103-8  Client 88cb-8794-332b disconnected from WLAN Wi-Fi.HK via HKU. Reason code is 8.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[6], 'Wi-Fi.HK via HKU' )
		self.assertEqual( arr[8], '' )
		self.assertEqual( arr[9], '8' )
		
	def test_row_info_dis_2(self):
		the_string = 'Jun  6 11:52:50 2016 info 147.8.123.17 HKU-H3C-WX6103-7  Client 3ca9-f481-5e60 disconnected from WLAN HKU. Reason code is 1.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[0], '06 6 11:52:50 2016' )
		self.assertEqual( arr[5], 'dis' )
		self.assertEqual( arr[6], 'HKU' )
		self.assertEqual( arr[7], '' )
	
	def test_row_info_dis_3(self):
		the_string = 'Jun  6 11:52:47 2016 info 147.8.123.17 HKU-H3C-WX6103-7  Client 1041-7fd4-475b disconnected from WLAN CSL Auto Connect. Reason code is 1.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[1], 'info' )
		self.assertEqual( arr[2], '147.8.123.17' )
		self.assertEqual( arr[6], 'CSL Auto Connect' )
		self.assertEqual( arr[9], '1' )	
		
	def test_row_info_roam_1(self):
		the_string = 'Jun  6 11:52:51 2016 info 147.8.123.18 HKU-H3C-WX6103-8  Client 9cd3-5bd5-fdc9 roamed from APID 149 with BSSID 3822-d61d-4860 of AC 127.0.0.1 to APID 150 with BSSID 3822-d61d-4850 of AC 127.0.0.1.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[6], '' )
		self.assertEqual( arr[10], '149' )
		self.assertEqual( arr[11], '3822-d61d-4860' )
		self.assertEqual( arr[12], '127.0.0.1' )
		
	def test_row_info_roam_2(self):
		the_string = 'Jun  6 11:52:50 2016 info 147.8.123.17 HKU-H3C-WX6103-7  Client 64cc-2e9e-757b roamed from APID 266 with BSSID 0023-8960-6a32 of AC 127.0.0.1 to APID 271 with BSSID 0023-895d-b222 of AC 127.0.0.1.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[2], '147.8.123.17' )
		self.assertEqual( arr[4], '64cc-2e9e-757b' )
		self.assertEqual( arr[5], 'rm' )
		self.assertEqual( arr[7], '271' )
		self.assertEqual( arr[8], '0023-895d-b222' )
		
	def test_row_info_Snyc_1(self):
		the_string = 'Jan  6 11:52:32 2016 info 147.8.123.17 HKU-H3C-WX6103-7 Synchronizing backup channel for APID 478 RadioId 2, changed from channel 6 to channel 11.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[0], '01 6 11:52:32 2016' )
		self.assertEqual( arr[5], 'bk' )
		self.assertEqual( arr[6], '' )
		self.assertEqual( arr[14], '2' )
		self.assertEqual( arr[16], '11' )
		
	def test_row_info_Snyc_2(self):
		the_string = 'Jan  6 11:52:30 2016 info 147.8.123.17 HKU-H3C-WX6103-7 Synchronizing backup channel for APID 356 RadioId 2, changed from channel 11 to channel 6.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[2], '147.8.123.17' )
		self.assertEqual( arr[4], '' )
		self.assertEqual( arr[7], '356' )
		self.assertEqual( arr[13], '' )
		self.assertEqual( arr[15], '11' )
		
	def test_row_info_change_1(self):
		the_string = 'Nov  6 11:51:33 2016 info 147.8.123.17 HKU-H3C-WX6103-7  Channel change for APID 140, RadioId 2 from channel 6 to channel 11.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[0], '11 6 11:51:33 2016' )
		self.assertEqual( arr[1], 'info' )
		self.assertEqual( arr[4], '' )
		self.assertEqual( arr[13], '' )
		self.assertEqual( arr[15], '6' )

	def test_row_info_change_2(self):
		the_string = 'Jun  6 11:51:33 2016 info 147.8.123.17 HKU-H3C-WX6103-7  Channel change for APID 582, RadioId 2 from channel 1 to channel 6.'
		arr = rawcsv.row_info( the_string.split() )
		self.assertEqual( arr[2], '147.8.123.17' )
		self.assertEqual( arr[7], '582' )
		self.assertEqual( arr[11], '' )
		self.assertEqual( arr[14], '2' )
		self.assertEqual( arr[16], '6' )

class TestRawcsv_warn(unittest.TestCase):
	
	def test_row_warn_interfere_1(self):
		the_string = 'Jun  6 11:52:40 2016 warning 147.8.123.17 HKU-H3C-WX6103-7 detected interfere(t): AP detected interfere :1.3.6.1.4.1.25506.2.75.2.3.0.8<hh3cDot11APMtIntfAPDetected> AP Serial Id:210235A0T6C126000174 Radio id:2 Channel Number:1 APMAC:00:1A:1E:83:10:A1'
		arr = rawcsv.row_warning( the_string.split() )
		self.assertEqual( arr[1], 'warn' )
		self.assertEqual( arr[2], '147.8.123.17' )
		self.assertEqual( arr[7], '' )
		self.assertEqual( arr[9], '' )
		self.assertEqual( arr[10], '' )
		self.assertEqual( arr[14], '2' )
		self.assertEqual( arr[15], '1' )
		self.assertEqual( arr[17], 'AP itf' )
		self.assertEqual( arr[18], '1.3.6.1.4.1.25506.2.75.2.3.0.8<hh3cDot11APMtIntfAPDetected>' )
		self.assertEqual( arr[19], '210235A0T6C126000174' )
		self.assertEqual( arr[20], '00:1A:1E:83:10:A1' )
	
	def test_row_warn_interfere_2(self):
		the_string = 'Jun  6 11:52:40 2016 warning 147.8.123.17 HKU-H3C-WX6103-7 detected interfere(t): Channel detected interfere :1.3.6.1.4.1.25506.2.75.2.3.0.7<hh3cDot11APMtChlIntfDetected> AP Serial Id:210235A0T6C126000174 Radio id:2 Channel Number:1'
		arr = rawcsv.row_warning( the_string.split() )
		self.assertEqual( arr[0], '6 6 11:52:40 2016' )
		self.assertEqual( arr[3], 'HKU-H3C-WX6103-7' )
		self.assertEqual( arr[13], '' )
		self.assertEqual( arr[15], '1' )
		self.assertEqual( arr[16], '' )
		self.assertEqual( arr[17], 'chl itf' )
		self.assertEqual( arr[18], '1.3.6.1.4.1.25506.2.75.2.3.0.7<hh3cDot11APMtChlIntfDetected>' )
		self.assertEqual( arr[19], '210235A0T6C126000174' )
	
	def test_row_warn_interfere_3(self):
		the_string = 'Jun  6 11:48:53 2016 warning 147.8.123.18 HKU-H3C-WX6103-8 detected interfere (t): Station detected interfere :1.3.6.1.4.1.25506.2.75.2.3.0.9<hh3cDot11APMtIntfStaDetected> AP Serial Id:210235A42MC115000038 Radio id:2 Channel Number:6 STAMAC:6C:72:E7:2E:43:76'
		arr = rawcsv.row_warning( the_string.split() )
		self.assertEqual( arr[3], 'HKU-H3C-WX6103-8' )
		self.assertEqual( arr[5], '' )
		self.assertEqual( arr[6], '' )
		self.assertEqual( arr[11], '' )
		self.assertEqual( arr[15], '6' )
		self.assertEqual( arr[17], 'STA itf' )
		self.assertEqual( arr[18], '1.3.6.1.4.1.25506.2.75.2.3.0.9<hh3cDot11APMtIntfStaDetected>' )
		self.assertEqual( arr[19], '210235A42MC115000038' )
		self.assertEqual( arr[21], '6C:72:E7:2E:43:76' )
		
def main():
	unittest.main()
		
if __name__ == '__main__':
	main()
	
	
	
	
	