import tkinter
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tkinter import *
import sys

def input_value():
    global basic_reward
    global final_reward
    items_cost.clear()
    try:
        for list, entries in zip(items_list_collection, entries_collection):
            item_cost = np.array([int(entry.get()) for entry in entries])
            items_cost.append(sum(item_cost * list["Cost"].to_numpy()))
        bonus = np.array([float(entry.get()) for entry in bonus_entries])
    except ValueError:
        sys.exit("QTY should be positive integer")
    final_reward = np.ceil(basic_reward * (1 + bonus))
    sol = minimize(lambda x:sum(x), x0, method='SLSQP', bounds=bnds,
                   constraints=cons)

    for i, name in enumerate(quiz_name):
        tkinter.Label(resultFrame, text=name).grid(row=i, column=0)
        tkinter.Label(resultFrame, text=np.ceil(sol.x[i])).grid(row=i, column=1)

def constraint1(x):
    return np.matmul(final_reward[0], x) - items_cost[0]
def constraint2(x):
    return np.matmul(final_reward[1], x) - items_cost[1]
def constraint3(x):
    return np.matmul(final_reward[2], x) - items_cost[2]
def constraint4(x):
    return np.matmul(final_reward[3], x) - items_cost[3]


items_name = ["item1", "item2", "item3", "item4"]
quiz_name = ["Q9", "Q10", "Q11", "Q12"]
items_list1 = pd.DataFrame({
    "Name": ["神名文字", "初級活動報告", "一般活動報告", "高級活動報告",
             "最高級活動報告", "基礎技術筆記（三一）", "一般技術筆記（三一）",
             "高級技術筆記（三一）", "最高級技術筆記（三一）", "傢俬", "現有"],
    "Cost": [25, 1, 10, 40, 200, 7, 12, 24, 60, 2000, -1],
    "pre_qty": [50, 300, 150, 70, 15, 75, 50, 35, 15, 1, 0]
})
items_list2 = pd.DataFrame({
    "Name": ['神名文字', '下級強化石', '一般強化石', '高級強化石',
             '最高級強化石', '基礎BD(三一)', '一般BD(三一)', '高級BD(三一)',
             '最高級BD(三一)', '傢俬', '現有'],
    "Cost": [20, 1, 4, 16, 64, 20, 40, 100, 200, 2000, -1],
    "pre_qty": [50, 300, 150, 70, 15, 45, 32, 24, 8, 1, 0]
})
items_list3 = pd.DataFrame({
    "Name": ['奧秘之書', '生鏽的擊針', '完好的擊針', '羅洪特抄本書頁',
             '羅洪特抄本書頁', '編輯過的羅洪特抄本', '完整的羅洪特抄本',
             '圖騰柱碎片', '破損的圖騰柱', '修復的圖騰柱', '完好的圖騰柱',
             '傢俬', '現有'],
    "Cost": [1000, 5, 25, 3, 10, 25, 50, 3, 10, 25, 50, 500, -1],
    "pre_qty": [1, 100, 40, 150, 60, 30, 15, 150, 60, 30, 15, 1, 0]
})
items_list4 = pd.DataFrame({
    "Name": ['Point', '現有'],
    "Cost": [1,-1],
    "pre_qty":[15000,0]
})
items_list_collection = [items_list1, items_list2, items_list3, items_list4]
entries_collection = []
basic_reward = np.array([
    [34, 0, 0, 7],
    [0, 29, 0, 6],
    [0, 0, 24, 5],
    [6, 6, 6, 16]
])
final_reward = basic_reward.copy()
bonus_entries = []
items_cost = [0,0,0,0]
bnds = [(0,1000) for _ in range(4)]
x0 = np.array([1,1,1,1])
con1 = {'type':'ineq', 'fun':constraint1}
con2 = {'type':'ineq', 'fun':constraint2}
con3 = {'type':'ineq', 'fun':constraint3}
con4 = {'type':'ineq', 'fun':constraint4}
cons = [con1, con2, con3, con4]

pd.set_option('display.unicode.east_asian_width', True)



root = Tk()

topFrame = Frame(root)
topFrame.pack(side=TOP)
midFrame = Frame(root)
midFrame.pack(side=LEFT)
resultFrame = Frame(root)
resultFrame.pack(side=LEFT)
botFrame = Frame(root)
botFrame.pack(side=RIGHT)
root.title("Entry Boxes")

for i, items_list in enumerate(items_list_collection):
    entry = []
    for j, (name, qty) in enumerate(zip(items_list["Name"], items_list["pre_qty"])):
        tkinter.Label(topFrame, text=name).grid(row=j, column=i * 2)
        my_entry = Entry(topFrame)
        my_entry.insert(0, qty)
        my_entry.grid(row=j, column=i * 2 + 1)
        entry.append(my_entry)
    entries_collection.append(entry)

for i, name in enumerate(items_name):
    tkinter.Label(midFrame, text=name).grid(row=i, column=0)
    my_entry = Entry(midFrame)
    my_entry.insert(0, 0)
    my_entry.grid(row=i, column=1)
    bonus_entries.append(my_entry)


my_button = Button(botFrame, text="Input", command=input_value)
my_button.pack()

root.mainloop()
