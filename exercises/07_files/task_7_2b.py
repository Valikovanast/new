# -*- coding: utf-8 -*-
"""
Задание 7.2b

Дополнить скрипт из задания 7.2a:
* вместо вывода на стандартный поток вывода,
  скрипт должен записать полученные строки в файл config_sw1_cleared.txt

При этом, должны быть отфильтрованы строки, которые содержатся в списке ignore.
Строки, которые начинаются на '!' отфильтровывать не нужно.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

ignore = ["duplex", "alias", "Current configuration"]
from sys import argv

file=open(argv[1],"r")
file1=open("config_sw1_cleared.txt","w")

for line in file:
  for i in ignore:
    if line.startswith('!') or i in line:
      break
  else:
      file1.write(line)
file.close()
file1.close()