from random import randint
import json

FIRST_NAME=['Joe', 'Paul', 'Allen', 'Jeremy', 'Jesicca', 'Maureen', 'Smith', 'Philips', 'Aldridge', 'Micheals', 'Kelly', 'Cool']

# from random import randint
# randint(0, 11)

SEPARATION=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J' 'K', 'L']

this_list = []
finish = 10
this_pk = 1
while this_pk < finish:
	this_dic = {}
	inner_dic = {}
	q=randint(0, 17)
	s= 'false'
	if q == 3:
		s='true'
	inner_dic['activity'] = FIRST_NAME[randint(0, 11)]+str(this_pk)
	inner_dic['no_longer_available'] = s
	this_dic['pk'] = str(this_pk)
	this_dic['model'] = 'staffer.StaffActivity,fields'
	this_dic['fields'] = inner_dic
	this_dic['pk'] = this_pk
	this_list.append(this_dic)
	this_pk += 1


with open('somefile.json', 'a') as the_file:
	the_file.write(json.dumps(this_list))
	# while this_pk < finish:
	# 	q=randint(0, 17)
	# 	s='false'
	# 	if q == 3:
	# 		s='true'
	# 	the_file.write('{"pk": '+str(this_pk)+',"model": "staffer.StaffActivity","fields": {"activity": "'+FIRST_NAME[randint(0, 11)]+str(this_pk)+'","no_longer_available": '+s+'}},')
	# 	this_pk += 1
	# the_file.write(']')

# this_list = 

# json.dumps(m)

	# {
 #        "pk": 2,
 #        "model": "sites.site",
 #        "fields": {
 #            "domain": "example.com",
 #            "name": "example.com"
 #        }
 #    }
