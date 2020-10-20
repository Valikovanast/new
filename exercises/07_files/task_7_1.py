# -*- coding: utf-8 -*-
"""
Задание 7.1

Обработать строки из файла ospf.txt и вывести информацию по каждой строке в таком виде:

Prefix                10.0.24.0/24
AD/Metric             110/41
Next-Hop              10.0.13.3
Last update           3d18h
Outbound Interface    FastEthernet0/0

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

new = "\n{:20} {}" *5

f=open('new/exercises/07_files/ospf.txt', 'r')
for line in f:

    line=line.split()
    print(new.format(
        "Prefix", line[1],
        "AD/Metric", line[2].replace("[","").replace("]",""),
        "Next-Hop", line[4].replace(",",""),
        "Last update", line[5].replace(",",""),
        "Outbound Interface", line[6],
        ))
f.close()