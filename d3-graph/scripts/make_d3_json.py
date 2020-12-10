import json

input_json_file_path = '../../draw_client_route/router_events.log'
input_group_movements_json_file_path = '../../draw_client_route/group_movements_output.json'
output_json_file_path = '../public/ap_roam_v1.json'

with open(input_json_file_path, 'r') as input_json_file, open(input_group_movements_json_file_path, 'r') as input_group_movements_json_file:
  input_json = json.loads(input_json_file.read())
  roam_from_to = input_json['Roaming']['matches']['apid_from_to']

  print("total count = %s, unique count = %s\n" % (len(roam_from_to), len(set(roam_from_to))))

  links = [ {
    "source": item[0].split('-')[0],
    "target": item[0].split('-')[1],
    "value": item[1]
  } for item in roam_from_to.items() ]

  apids = []
  for link in links:
    apids.append(link['source'])
    apids.append(link['target'])

  apids = set(apids)

  print("apid count = %s" % (len(apids)))

  nodes = [ {
    "id": apid,
    "group": round(int(apid) / 5)
  } for index, apid in enumerate(apids) ]

  print(nodes[:10])
  print(links[:10])

  group_movements = json.loads(input_group_movements_json_file.read())['group_movements']
  group_movements = [ {
    'clients': len(m['clients']),
    'path': m['path']
  } for m in group_movements ]

  with open(output_json_file_path, 'w') as output_json_file:
    json.dump({
      "nodes": nodes,
      "links": links,
      "group_movements": group_movements
    }, output_json_file)

