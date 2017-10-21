import time
import moviedb2

if not moviedb2.load_config ( "config.yml" ):
    exit()

print ("Watching folder: {}".format ( moviedb2.CONFIG["PATH"] ))
while 1:
  status = moviedb2.monitor_folder ( moviedb2.CONFIG["PATH"] )
  if status > 0:
      print("New files: {}".format(status), end='\r')
  time.sleep (10)
