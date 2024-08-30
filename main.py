from functions import *
if checkFileExistence("data.txt"):
  main()
else:
  setup()
  main()