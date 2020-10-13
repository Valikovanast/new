# -*- coding: utf-8 -*-
"""
Задание 5.2b

Преобразовать скрипт из задания 5.2a таким образом,
чтобы сеть/маска не запрашивались у пользователя,
а передавались как аргумент скрипту.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""
from sys import argv

net=argv[1].split('.')
masko=net[3].split('/')
mask1=masko[1]
mask=masko[1]
mask=int(mask)*"1"+"0"*(32-int(mask))
mask2=mask[:8]
mask3=mask[8:16]
mask4=mask[16:24]
mask5=mask[24:]
net0=bin(int(net[0])&int(mask2,2))[2:]
net[0]=int(net0,2)
net1=bin(int(net[1])&int(mask3,2))[2:]
net[1]=int(net1,2)
net2=bin(int(net[2])&int(mask4,2))[2:]
net[2]=int(net2,2)
net3=bin(int(masko[0])&int(mask5,2))[2:]
net[3]=int(net3,2)
print("Network:\n"+'{:d}\t\t{:d}\t\t{:d}\t\t{:d}\n'.format(int(net0,2),int(net1,2),int(net2,2),int(net3,2))+'{:08b}\t{:08b}\t{:08b}\t{:08b}\n\n'.format(int(net[0]),int(net[1]),int(net[2]),int(net[3]))+
"Mask:\n/"+mask1+'\n{:d}\t\t{:d}\t\t{:d}\t\t{:d}\n'.format(int(mask2,2),int(mask3,2),int(mask4,2),int(mask5,2))+
mask2+"\t"+mask3+"\t"+mask4+"\t"+mask5+"\n")