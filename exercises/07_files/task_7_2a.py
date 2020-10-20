# -*- coding: utf-8 -*-
"""
Задание 7.2a

Сделать копию скрипта задания 7.2.

Дополнить скрипт:
  Скрипт не должен выводить команды, в которых содержатся слова,
  которые указаны в списке ignore.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

from sys import argv
ignore = ["duplex", "alias", "Current configuration"]
file=open(argv[1],"r")

for line in file:
  for i in ignore:
    if line.startswith('!') or i in line:
      break
  else:
    print(line.rstrip())
file.close()
