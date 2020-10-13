# -*- coding: utf-8 -*-
"""
Задание 4.6

Обработать строку ospf_route и вывести информацию на стандартный поток вывода в виде:
Prefix                10.0.24.0/24
AD/Metric             110/41
Next-Hop              10.0.13.3
Last update           3d18h
Outbound Interface    FastEthernet0/0

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

ospf_route = "      10.0.24.0/24 [110/41] via 10.0.13.3, 3d18h, FastEthernet0/0"
a= ospf_route.strip()
a=a.split()
a1=a[1].strip('[]')
a3=a[3].strip(',')
a4=a[4].strip(',')
print("Prefix\t\t\t\t"+a[0]+"\nAD/Metric\t\t\t"+a1+"\nNext-Hop\t\t\t"+a3+"\nLast update\t\t\t"+a4+"\nOutbound Interface\t\t"+a[-1])

