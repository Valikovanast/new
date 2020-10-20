# -*- coding: utf-8 -*-
"""
Задание 7.3b

Сделать копию скрипта задания 7.3a.

Переделать скрипт:
- Запросить у пользователя ввод номера VLAN.
- Выводить информацию только по указанному VLAN.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""
file= open("new/exercises/07_files/CAM_table.txt", "r")
vlan=input("Введите vlan: ")
new=list()
for f in file:
    tb = f.split()
    if len(tb) == 4 and tb[0].isdigit() and tb[0]==vlan:
        new.append([int(tb[0]),tb[1],tb[3]])
for a,b,c in sorted(new):
    print(str(a)+"\t"+b+"\t"+c)
file.close()