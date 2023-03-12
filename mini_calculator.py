import tkinter
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tkinter import *
from tkinter import ttk
import sys
import os

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
    files = sorted([name for name in os.listdir(os.path.join(event_dir, selected_event.get()))\
             if name[0].isnumeric() and name.endswith(".csv")])
    for file in files:
        items_list_collection.append(pd.read_csv(os.path.join(event_dir, selected_event.get(), file)))
    df = os.path.join(event_dir, selected_event.get(), "basic_reward.csv")
    basic_reward = (np.loadtxt(open(df),delimiter=","))

    bonus_entries = []
    items_cost = [0 for _ in range(len(files))]

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

    for i, name in enumerate(files):
        tkinter.Label(midFrame, text=name[2:-4]).grid(row=i, column=0)
        my_entry = Entry(midFrame)
        my_entry.insert("0", "0")
        my_entry.grid(row=i, column=1)
        bonus_entries.append(my_entry)

    #Setting for scipy minimize
    bnds = [(0, 1000) for _ in range(4)]
    x0 = np.array([1, 1, 1, 1])

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
        final_reward = np.ceil(np.array([basic_reward[i] * (1 + bonus[i]) for i in range(len(bonus))]))
        cons = [{'type': 'ineq', 'fun': lambda x, coef=i: np.matmul(final_reward[coef], x) - items_cost[coef]} for i in
                range(len(files))]
        sol = minimize(lambda x: sum(x), x0, method='SLSQP', bounds=bnds,
                       constraints=cons)

        for i, name in enumerate(quiz_name):
            tkinter.Label(resultFrame, text=name).grid(row=i, column=0)
            tkinter.Label(resultFrame, text=np.ceil(sol.x[i])).grid(row=i, column=1)

    my_button = Button(botFrame, text="Input", command=input_value)
    my_button.pack()

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
event_dir = os.path.join(os.path.dirname(__file__), 'event')
event_cb['values'] = [name for name in os.listdir(event_dir) if name != ".DS_Store"]
event_cb['state'] = 'readonly'
event_cb.pack(side=TOP)

#Create second form for collect entry and calculation
event_cb.bind("<<ComboboxSelected>>",create_form)

root.mainloop()
