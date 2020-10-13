# -*- coding: utf-8 -*-
"""
Задание 6.2b

Сделать копию скрипта задания 6.2a.

Дополнить скрипт:
Если адрес был введен неправильно, запросить адрес снова.

Ограничение: Все задания надо выполнять используя только пройденные темы.
"""
a = input("Введите IP-адрес(10.0.1.1):")
a1= a.split('.')

while len(a1)!=4 or not (int(a1[0]) in range(0,256) and int(a1[1]) in range(0,256) and int(a1[2]) in range(0,256) and int(a1[3]) in range(0,256)):
   print("Неправильный IP-адрес")
   a = input("Введите IP-адрес(10.0.1.1):")
   a1= a.split('.')
if int(a1[0]) in range(1,224):
   print("unicast")
elif int(a1[0]) in range(224,241):
   print("multicast")
elif a=='255.255.255.255':
   print("local broadcast")
elif a=='0.0.0.0':
   print("unassigned")
else:
   print("unused")