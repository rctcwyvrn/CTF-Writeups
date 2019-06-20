import codecs
import math
import itertools
from binascii import unhexlify

def hex_to_base64(hex_in):
	raw = codecs.decode(hex_in,'hex')
	return codecs.encode(raw,'base64').decode()

def fixed_xor(raw1, raw2):
	out = b''
	for i in range(len(raw1)):
		out += bytes([raw1[i] ^ raw2[i]])
	return out

def single_byte_xor(in_hex, char_val):
	raw = codecs.decode(in_hex,'hex')
	out = b''
	for byte in raw:
		out += bytes([byte ^ char_val])
	return out


def get_score(input_bytes):
	character_frequencies = {
	'a': .08167, 'b': .01492, 'c': .02782, 'd': .04253,
	'e': .12702, 'f': .02228, 'g': .02015, 'h': .06094,
	'i': .06094, 'j': .00153, 'k': .00772, 'l': .04025,
	'm': .02406, 'n': .06749, 'o': .07507, 'p': .01929,
	'q': .00095, 'r': .05987, 's': .06327, 't': .09056,
	'u': .02758, 'v': .00978, 'w': .02360, 'x': .00150,
	'y': .01974, 'z': .00074, ' ': .13000
	}

	# Initialize variable to store each value of each character. 
	scores = []
	# Iterate over each character and make each character lowercase
	for byte in (input_bytes):
		# Change the byte value to a string, and look up the 
		# character in the character_frequencies variable. If the
		# character doesn’t exist in the dictionary, make the value 0.
		score = character_frequencies.get(chr(byte).lower(), 0)
		# Add the score to the list of scores
		scores.append(score)
		# Sum and return the score
	return sum(scores)

def break_single_byte_xor(in_hex):
	potential_messages = []
	for i in range(256):
		res = single_byte_xor(in_hex,i)
		score = get_score(res)
		data = {
			'message' : res,
			'score' : score,
			'key' : i
		}
		potential_messages.append(data)
	sorted_messages = sorted(potential_messages, key=lambda x: x['score'], reverse=True)
	#print("best result:",sorted_messages[0])
	return sorted_messages[0]

def break_single_byte_xor_file(file):
	potential_messages = []
	for line in file:
		line = line.strip()
		res = break_single_byte_xor(line)
		potential_messages.append(res)
	sorted_messages = sorted(potential_messages, key=lambda x: x['score'], reverse=True)
	#print("best result:",sorted_messages[0])
	return sorted_messages[0]

def repeating_key_xor(plaintext, key):
	bytes_in = b''
	for char in plaintext:
		bytes_in+= bytes([ord(char)])
	out = b''
	count = 0
	for byte in bytes_in:
		out += bytes([ord(key[count]) ^ byte])
		count+=1 
		count = count % len(key)
	return out

def hdist(str1,str2):
	bytes1 = bytes(str1,'ascii')
	bytes2 = bytes(str2,'ascii')
	return hdist(bytes1,bytes2)

def hdist(bytes1,bytes2):
	count=0
	for i in range(len(bytes2)):
		bits1 = "{0:b}".format(bytes1[i])
		bits2 = "{0:b}".format(bytes2[i])
		for a in range(min(len(bits1),len(bits2))):
			if(bits1[len(bits1)-a-1] != bits2[len(bits2)-a-1]): 
				count+=1

		count += abs(len(bits1)-len(bits2))
	return count


def blockify(in_bytes, block_size):
	blocks = []
	x = 0;
	for i in range(math.floor(len(in_bytes) / block_size)):
		blocks.append(take_block(in_bytes, x, x+block_size))
		x+=block_size
	return blocks

def take_block(in_bytes, a, b):
	out = b''
	for i in range(a,b):
		out+=bytes([in_bytes[i]])
	return out

def transpose(blocks):
	out = []
	for i in range(len(blocks[0])):
		new_column=[]
		for block in blocks:
			new_column.append(block[i])
		out.append(new_column)
	return out


def break_repeating_key_xor_hex(hex_in,guess_len):
	return break_repeating_key_xor(codecs.decode(hex_in,'hex'),guess_len)


def break_repeating_key_xor_file(file,guess_len):
	lines = file.read().strip()
	enc_bytes = codecs.decode(lines.encode(),'base64')
	return break_repeating_key_xor(enc_bytes,guess_len)

def break_repeating_key_xor(enc_bytes,guess_len):
	potential_lengths = []
	guess_len +=1
	for key_size in range(2,guess_len):
		chunks=blockify(enc_bytes,key_size)
		norm_dists = [
			hdist(pair[0],pair[1])
			for pair in itertools.combinations(chunks,2)
		]
		dist = sum(norm_dists)/len(norm_dists)
		dist = dist/float(key_size)
		data = {
			'key_size':key_size,
			'dist':dist
		}
		potential_lengths.append(data)

	sorted_lengths = sorted(potential_lengths, key=lambda x: x['dist'],reverse=False)
	print("best length = ",sorted_lengths[0])

	best_key_len = sorted_lengths[0]['key_size']
	blocks = blockify(enc_bytes,best_key_len)
	trans = transpose(blocks)
	final_key = []
	for columnn in trans:
		columnn = (bytes(columnn))
		#print(columnn)
		key = break_single_byte_xor(codecs.encode(columnn,'hex'))['key']
		final_key.append(key)
	ascii_key = []
	for a in final_key:
		ascii_key.append(chr(a))

	key = ''.join(ascii_key)
	return key

def is_ecb(in_bytes):
	blocks = blockify(in_bytes,16)
	lenA = len(blocks)
	#lenB will be smaller than lenA if blocks has duplicates in it
	lenB = len(list(set(blocks)))
	return lenA != lenB

def detect_aes(file):
	lines = file.readlines()
	enc = []
	for line in lines:
		enc.append(unhexlify(line.strip()))
	count = 0
	possible_ecb = []
	for line in enc:
		if(is_ecb(line)):
			possible_ecb.append(line)
		count +=1
	return possible_ecb


# res= detect_aes(open("8.txt","r"))
# print("possible messages:")
# for a in res:
# 	print("message:",codecs.encode(a,'hex'))