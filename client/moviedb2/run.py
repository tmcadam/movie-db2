import time
import sys
import datetime

import moviedb2

if not moviedb2.load_config ( "config.yml" ):
    exit()

print ("Watching folder: {}".format ( moviedb2.CONFIG["PATH"] ))
while 1:
  folder_stats = moviedb2.monitor_folder ( moviedb2.CONFIG["PATH"], moviedb2.CONFIG["DATA_PATH"] )
  if folder_stats:
      print("{3} :-> Count: {0}    Found: {1}    Sent: {2}".format(folder_stats["count"],
                                                            folder_stats["found"],
                                                            folder_stats["sent"],
                                                            datetime.datetime.now()))
  else:
      print("{0} :-> Error".format(datetime.datetime.now()))
  time.sleep (10)
