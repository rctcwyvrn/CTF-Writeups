import requests

url = "https://bnv.web.ctfcompetition.com/api/search"
headers = {'Content-type':'application/json'}

def blind(message):
	message = message.lower();

	blindvalues = [
	'10',    '120',   '140',    '1450',   '150',   '1240',  '12450',
	'1250',  '240',   '2450',   '130',    '1230',  '1340',  '13450',
	'1350',  '12340', '123450', '12350',  '2340',  '23450', '1360',
	'12360', '24560', '13460',  '134560', '13560']

	
	blindmap = {}
	i=0
	message_new = '';

	test=['1']*97 #If we can figure out what smaller values work for the blinding function then we can possibly run an injection attack?

	blindvalues = test+ blindvalues

	for blind_val in blindvalues:
		blindmap[i] = blind_val
		i+=1

	#print(blindmap)
	for i in range(len(message)):
		message_new += blindmap[ord(message[i])];

	print("blinded message=",message_new) 
	return message_new



test = {
	'message':blind("zurich")
}

req= requests.post(url,json=test,headers=headers)

print("code =",req.status_code)
print("response =",req.text)

test = {
	'message':str(100**1000)
}

print("SENDING THIS MONSTROSITY",test)
req= requests.post(url,json=test,headers=headers)

print("code =",req.status_code)
print("response =",req.text)


# print("sending blinds in a really stupid brute force method")
# for i in range(10**3):
# 	print("sending message=",i)
# 	test = {
# 		'message':str(i)
# 	}
# 	req= requests.post(url,json=test,headers=headers)
# 	if req.text.find("No result found") == -1:
# 		print(req.text)
# 		break