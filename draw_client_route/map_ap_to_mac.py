import re, json
import comlo

output_file_path = './map_aps.json'

# regex_location = 'AP Name:([\w_]+) '
regex_location = 'AP Name:([\w_]+) BSSID:((?:[\w]{2}:?){6})'
regex_mac_to_apid = 'APID (\d+) with BSSID ((?:[0-9a-f]{4}-){2}[0-9a-f]{4})'

mac_location = {}
mac_apid = {}

access_points_by_mac = {}
access_points = []

def get_merge_dist(d1, d2):
  _d1 = d1.copy()
  _d2 = d2.copy()
  _d1.update(_d2)
  return _d1

with comlo.terfread('1118wx/comf', max_iter=-1) as log_file:
  for line in log_file:
    re_matches = re.findall(regex_location, line)
    if len(re_matches) != 0:
      for location_mac_pair in re_matches:
        location = location_mac_pair[0]
        mac = ''.join(location_mac_pair[1].split(':')).lower()

        if not mac in mac_location:
          mac_location[mac] = {
            'location': location
          }
        else:
          if mac_location[mac]['location'] != location:
            print("unmatched %s vs %s" % (mac_location[mac], location))
          else:
            pass
            # print(".", end="")
        continue
    
    re_matches = re.findall(regex_mac_to_apid, line)
    if len(re_matches) != 0:
      for apid_mac_pair in re_matches:
        apid = apid_mac_pair[0]
        mac = ''.join(apid_mac_pair[1].split('-')).lower()

        if not mac in mac_apid:
          mac_apid[mac] = {
            'apid': apid
          }
        else:
          if mac_apid[mac]['apid'] != apid:
            print("unmatched %s vs %s" % (mac_apid[mac], apid))
          else:
            pass
            # print("'", end="")


  print("Got %s ap from filtering location" % len(mac_location))
  print("Got %s ap from filtering apid" % len(mac_apid))

  print("\nStart mapping the access points")

  all_mac_set = [mac_location, mac_apid]

  for mac_set in all_mac_set:
    for mac_mapping in mac_set.items():
      mac = mac_mapping[0]
      attrs = mac_mapping[1]

      if not mac in access_points_by_mac:
        access_points_by_mac[mac] = attrs
      else:
        origin_attrs = access_points_by_mac[mac]
        attrs_keys = list(attrs.keys())

        is_not_overlapped = True
        for origin_attrs_key in origin_attrs.keys():
          if origin_attrs_key in attrs_keys:
            print('overlapped attr key')
            print('%s -> %s' % (origin_attrs, attrs))
            is_not_overlapped = False

        if is_not_overlapped:
          access_points_by_mac[mac].update(attrs)
        else:
          print('overlapped at %s' % mac)

  print("distinct ap = %s" % len(access_points_by_mac))
  # print(access_points_by_mac)

  access_points = [ get_merge_dist(mac_attrs_pair[1], {
      'mac': mac_attrs_pair[0],
    }) for mac_attrs_pair in access_points_by_mac.items() ]

  print("Got %s ap in total\n" % len(access_points))
  attrs_to_check = ['mac', 'apid', 'location']

  for attr in attrs_to_check:
    access_points_set = set([ ap[attr] if attr in ap else None for ap in access_points ])
    if None in access_points_set:
      access_points_set.remove(None)
    print("%s set has %s" % (attr, len(access_points_set)))

  with open(output_file_path, 'w') as output_file:
    json.dump({
      'access_points': access_points,
      # 'mac_to_index': access_points_by_mac_and_index
    }, output_file)
    output_file.close()
  
