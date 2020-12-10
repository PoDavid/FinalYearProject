import re, json, copy, sys
import comlo

from router_events_const import Router_Events_Const

keywords = Router_Events_Const.KEYWORDS
skip_lines = Router_Events_Const.SKIP_LINES

max_iter = -1
if len(sys.argv) >= 2:
  max_iter = int(sys.argv[1])
  print('running with ' + str(max_iter))
with comlo.terfread('1118wx/comf', max_iter=max_iter) as log_file:
  events = {}
  count = 0
  extra_warning_count = 0
  for line in log_file:
    count += 1
    is_found = False

    # _k is the key of each object
    # k is the display name for the object
    for _k, v in keywords.items():

      k = v['name']
      if _k in line:
        is_found = True
        if k in events:
          events[k]['count'] += 1
          events[k]['lines'].append(line)

          for _name, (_re, _g) in v['re'].items():
            # print(line)
            if not _name in events[k]['matches']:
              events[k]['matches'][_name] = {}

            re_matches = re.findall(_re, line)
            if len(re_matches) == 0:
              # print(_name, _k)
              continue

            match = str(re_matches[0])

            # join the results if there are multiple matches
            if len(re_matches[0]) > 1:
              if isinstance(re_matches[0], tuple):
                match = "-".join(list(re_matches[0]))
            
            if match in events[k]['matches'][_name]:
              events[k]['matches'][_name][match] += 1
            else:
              events[k]['matches'][_name][match] = 1
        else:
          events[k] = {
            'count': 0,
            'lines': [],
            'matches': {}
          }

    if not is_found:
      # there is a general warning line which is 60 characters long
      # use this hack to skip it
      if not len(line) is 60 and 'warning' not in line:
        print(line)
      else:
        extra_warning_count += 1
        

  print('all lines')
  print(count)
  print('skipping general warnings')
  print(extra_warning_count)
  print('')

  for k, v in events.items():

    print("Analysis for {:s}({:d}):".format(k, v['count']))
    count -= v['count']
    if len(v['matches']) == 0:
      print("Nothing to show. Skip this.\n")
      continue

    for _name, _matches in v['matches'].items():
      if len(_matches) > 0:
        sorted_matches = sorted(_matches.items(), key=lambda x: x[1], reverse=True)
        print(_name, sorted_matches[:10])

    print()

  print(count - extra_warning_count)

  # skip the lines attributes for output
  events_copy = copy.deepcopy(events)
  for k, v in events.items():
    events_copy[k].pop('lines', None)

  # write the log
  output_file = open('router_events.log', '+w')
  output_file.write(json.dumps(events_copy))
  output_file.close()


