import time
import sys
import hashlib, uuid
import random
import requests
import re
#### This block is mandatory for our system
offset = int(sys.argv[1])
limit = int(sys.argv[2])
####

courses = ['CMPE140','CMPE150','CMPE210','CMPE220','CMPE250','CMPE300','CMPE322',
		   'CMPE343','CMPE344','CMPE350','CMPE422','CMPE425','CMPE434','CMPE436',
		   'CMPE443','CMPE446','CMPE451','CMPE451','CMPE475','CMPE480','CMPE483',
		   'CMPE487','CMPE489','CMPE491','CMPE492','CMPE49F','CMPE511','CMPE521',
		   'CMPE530','CMPE537','CMPE547','CMPE561','CMPE579','CMPE581','CMPE58C',
		   'CMPE58D','CMPE58H','CMPE58S','CMPE595']

url = 'http://registration.boun.edu.tr/scripts/quotasearch.asp'
for i in range(offset,offset+limit,1):
	body = {
		'abbr': courses[i][:4],
		'code': courses[i][-3:],
		'section': "01"
		}
	r = requests.post(url=url, data = body)
	result = re.search('Max\. Classroom Capacity:</b> (\d+)<br>',r.text)
	##### Printing the result is also mandatory
	print("Capacity for course: " + courses[i] +" is: " + result.group(1))
	##### As we capture the output from stdout




