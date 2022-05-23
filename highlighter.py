import re

x = open('/Volumes/Kindle/documents/My Clippings.txt')

line = x.readline()
lines = 0
test = {}

# line = x.readline()
# line = x.readline()
# line = x.readline()

while line:
    lines += 1
    # print(line)
    line = x.readline()
    print(line)



x.close()
