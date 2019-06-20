import codecs

flag = "6f636970 7b465443 5f624467 735f5369 72337055 3335755f 5f4c7566 61616665 39326232 0000007d"

parts = flag.split()
out = ""
for part in parts:
	print(codecs.decode(part,'hex'))

print(out)