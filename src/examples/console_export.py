import time
from kritter.kterm import Kterm

'''
This is an example of using Kterm to export stdout to browser. 
Run this and then point your browser to http:<hostname>:5000
'''
Kterm(None, name="Console example") 

i = 0
while True:
    print(f"Message {i}")
    i += 1
    time.sleep(1)