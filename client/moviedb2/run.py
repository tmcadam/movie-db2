import time
import moviedb2

if not moviedb2.load_config ( "config.yml" ):
    exit()

print ("Watching folder: {}".format ( moviedb2.CONFIG["PATH"] ))
while 1:
  folder_stats = moviedb2.monitor_folder ( moviedb2.CONFIG["PATH"], moviedb2.CONFIG["DATA_PATH"] )
  if folder_stats:
      print("Count: {}    Found: {}    Sent: {}".format(folder_stats["count"], folder_stats["found"], folder_stats["sent"]), end='\r')
  else:
      print("Error", end='\r')
  time.sleep (10)
