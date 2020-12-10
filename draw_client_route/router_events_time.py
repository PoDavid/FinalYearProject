import json
import comlo
import log_helper as H

from router_events_const import Router_Events_Const

keywords = Router_Events_Const.KEYWORDS
skip_lines = Router_Events_Const.SKIP_LINES

active_keywords = [
  'successfully joins', 'Deassociate(t):', 'detected interfere(t)',
  'Disconnect(t)', 'disconnected from', '; User got online successfully',
  'User logged off.'
]

# store the timestamps in order
# timestamp_list = []

# index by timestamp
event_dict = {}

max_iter = -1
with comlo.terfread('1118wx/comf', max_iter=max_iter) as log_file, open('router_events_time.json', 'w') as output_file:
  for line in log_file:
    for keyword in active_keywords:
      if keyword in line:
        # parse timestamp
        timestamp = H.parseToTimeFromEpoch(line)
        if timestamp not in event_dict:
          event_dict[timestamp] = {
            'events': { }
          }

        if keyword not in event_dict[timestamp]['events']:
          event_dict[timestamp]['events'][keyword] = 0

        event_dict[timestamp]['events'][keyword] += 1

  
  output_file.write(json.dumps({
    'event_dict': event_dict
  }))
  output_file.close()
  # H.pr(event_dict)
  # print(event_dict)


