#lETS GOOOOo
#I have 2 hours before boarding my flight, lets see what we can do!
import set_1, set_2
import os

def cbc_mac(msg, IV, key):
	return set_2.aes_cbc_mode_enc(msg, IV, key)[-16:]

server_key = os.urandom(16)
def cbc_mac_server(message, IV, MAC):
	check = cbc_mac(message, IV, server_key) == MAC
	if not check:
		print("MAC FAILED!!! REJECTING")
		print("actual",cbc_mac(message, IV, server_key),"got", MAC)
		return
	else:
		parts = message.decode().split("&")
		msg_from = parts[0]
		msg_to = parts[1]
		msg_amount = parts[2]

		print('MAC SUCCESS!!!')
		print(f"Moving {msg_amount} from {msg_from} to {msg_to}")

def cbc_mac_server_v2(message, MAC):
	actual = cbc_mac(message, b'\x00'*16, server_key)
	check = actual == MAC
	if not check:
		print("MAC FAILED!!! REJECTING")
		print("actual",actual,"got", MAC)
		return
	else:
		parts = message.decode().split("&")
		msg_from = parts[0]
		msg_list = parts[1]

		print('MAC SUCCESS!!!')
		print(f"Moving from {msg_from} to {msg_list}")


def challenge_49():
	#part 1
	msg = b'from=#{howard}&to=#{howard}&amount=#{10000 space dollars}'
	test_mac = cbc_mac(msg, b'\x00'*16, server_key) #stealing one valid mac that we could have sent
	cbc_mac_server(msg, b'\x00'*16, test_mac)
	cbc_mac_server(b'no u'*20, b'\x00'*16, test_mac) #test

	print(len(msg), msg[:16])
	forge = b'from=#{google}&t' + msg[16:]
	forge_IV = set_1.fixed_xor(b'from=#{google}&t', b'from=#{howard}&t') #EZCLAP
	cbc_mac_server(forge, forge_IV, test_mac)


	#part 2
	valid_payment = b'from={google}&tx_list=howard:10;' #google refunding me for some in app purchases my cat made 
	print(len(valid_payment)) #32 byte message to avoid stupid padding stuff
	valid_mac = cbc_mac(valid_payment, b'\x00'*16, server_key)
	cbc_mac_server_v2(valid_payment,valid_mac)

	dummy = b'from={}&tx_list=howard:10000000;'
	print(len(dummy))
	dummy_mac = cbc_mac(dummy, b'\x00'*16, server_key)
	cbc_mac_server_v2(dummy,dummy_mac)
	print("dummy",dummy_mac)

	#we want to append the last block of hte valid_payment to make it use our known MAC

	evil = valid_payment + set_1.fixed_xor(set_2.aes_block_dec(b'\x00'*16,server_key), valid_mac) + dummy[-16:]
	print(evil)
	print("should be 0",set_2.aes_block_enc(set_2.aes_block_dec(b'\x00'*16,server_key),server_key))
	cbc_mac_server_v2(evil,dummy_mac)




	#MAC = E(last block XOR previous encryption res)
	#if we make our new last message block x
	#then new MAC = E(x XOR MAC) and we want to make x an extra transaction to me

	#how do we length extend this attack?
	#we want to take the valid_mac, and use it as an iV to continue the msg to append on ;howard:10000000 <- 16 bytes
	#it would be easy if I could just do cbc_encrypt(extension, iv=valid_mac, key=server_key) but we don't have server_key...


challenge_49()