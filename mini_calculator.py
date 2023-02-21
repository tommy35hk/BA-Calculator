import tkinter
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tkinter import *
from tkinter import ttk
import sys
import os

items_name = ["item1", "item2", "item3", "item4"]
quiz_name = ["Q9", "Q10", "Q11", "Q12"]

pd.set_option('display.unicode.east_asian_width', True)


#Create first window for Combobox, user can select the event they need
root = Tk()
root.resizable(False,False)
root.title("BA Calculator")
label = ttk.Label(text="Please select an event:")
label.pack(side=TOP)
selected_event = tkinter.StringVar()
event_cb = ttk.Combobox(root, textvariable=selected_event)
#Option in Combobox will be based on the file we have
event_cb['values'] = [name for name in os.listdir() if os.path.isdir(name)
                      and name != ".git"]
event_cb['state'] = 'readonly'
event_cb.pack(side=TOP)

#Create second form for collect entry and calculation
def create_form(event):
    result = Toplevel(root)
    topFrame = Frame(result)
    topFrame.pack(side=TOP)
    midFrame = Frame(result)
    midFrame.pack(side=LEFT)
    resultFrame = Frame(result)
    resultFrame.pack(side=LEFT)
    botFrame = Frame(result)
    botFrame.pack(side=RIGHT)
    result.title(selected_event.get())

    items_list_collection = []
    entries_collection = []
    #Fill data from the folder selected
    for file in ["item1.csv", "item2.csv", "item3.csv", "item4.csv"]:
        items_list_collection.append(pd.read_csv(os.path.join(selected_event.get(), file)))
    df = os.path.join(selected_event.get(),"basic_reward.csv")
    basic_reward = (np.loadtxt(open(df),delimiter=","))
    final_reward = basic_reward.copy()
    bonus_entries = []
    items_cost = [0, 0, 0, 0]

    #Create forms based on the data input
    for i, items_list in enumerate(items_list_collection):
        entry = []
        for j, (name, qty) in enumerate(zip(items_list["Name"], items_list["start_qty"])):
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

    #Setting for scipy minimize
    def constraint1(x):
        return np.matmul(final_reward[0], x) - items_cost[0]

    def constraint2(x):
        return np.matmul(final_reward[1], x) - items_cost[1]

    def constraint3(x):
        return np.matmul(final_reward[2], x) - items_cost[2]

    def constraint4(x):
        return np.matmul(final_reward[3], x) - items_cost[3]

    bnds = [(0, 1000) for _ in range(4)]
    x0 = np.array([1, 1, 1, 1])
    con1 = {'type': 'ineq', 'fun': constraint1}
    con2 = {'type': 'ineq', 'fun': constraint2}
    con3 = {'type': 'ineq', 'fun': constraint3}
    con4 = {'type': 'ineq', 'fun': constraint4}
    cons = [con1, con2, con3, con4]

    #Collect user entries and do calculation
    def input_value():
        items_cost.clear()
        try:
            for list, entries in zip(items_list_collection, entries_collection):
                item_cost = np.array([int(entry.get()) for entry in entries])
                items_cost.append(sum(item_cost * list["Cost"].to_numpy()))
            bonus = np.array([float(entry.get()) for entry in bonus_entries])
        except ValueError:
            sys.exit("QTY should be positive integer")
        final_reward = np.ceil(basic_reward * (1 + bonus))
        sol = minimize(lambda x: sum(x), x0, method='SLSQP', bounds=bnds,
                       constraints=cons)

        for i, name in enumerate(quiz_name):
            tkinter.Label(resultFrame, text=name).grid(row=i, column=0)
            tkinter.Label(resultFrame, text=np.ceil(sol.x[i])).grid(row=i, column=1)

    my_button = Button(botFrame, text="Input", command=input_value)
    my_button.pack()

event_cb.bind("<<ComboboxSelected>>",create_form)

root.mainloop()
