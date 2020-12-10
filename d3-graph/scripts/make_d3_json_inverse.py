import json

input_json_file_path = '../../draw_client_route/router_events.log'
input_group_movements_json_file_path = '../../draw_client_route/group_movements_output.json'
output_json_file_path = '../public/ap_roam_v2.json'

with open(input_json_file_path, 'r') as input_json_file, open(input_group_movements_json_file_path, 'r') as input_group_movements_json_file:
  input_json = json.loads(input_json_file.read())
  roam_from_to = input_json['Roaming']['matches']['apid_from_to']

  client_passed_by_time = json.loads(input_group_movements_json_file.read())['client_passed_by_time']

  links_dist = {}
  nodes_dist = {}
  for _, path_to_clients in client_passed_by_time.items():
    for path, clients in path_to_clients.items():
      
      # print(path, clients)
      client_pairs = [ (client_a, client_b) for client_a in clients for client_b in clients if client_a != client_b and client_a < client_b ]
      for pair in client_pairs:
        # print(pair)

        pair_list = list(pair)
        # add the node
        for client in pair_list:
          if client not in nodes_dist:
            nodes_dist[client] = []
          if path not in nodes_dist[client]:
            nodes_dist[client].append(path)
          

        # add the link
        link_id = '<->'.join(pair_list)
        if link_id not in links_dist:
          links_dist[link_id] = []

        if path not in links_dist[link_id]:
          links_dist[link_id].append(path)

  # print(links_dist, nodes_dist)
  with open(output_json_file_path, 'w') as output_json_file:
    json.dump({
      "nodes": [ {
        "group": len(node[1]),
        "id": node[0]
      } for node in nodes_dist.items() ],
      "links": [ {
        "source": link[0].split('<->')[0],
        "target": link[0].split('<->')[1],
        "value": len(link[1]),
      } for link in links_dist.items() ]
    }, output_json_file)
