import tkinter
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tkinter import *
from tkinter import ttk
import sys
import os

class calculator(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.resizable(False,False)
        self.title("BA Calculator")
        label = ttk.Label(text="Please select an event: ")
        label.pack(side=TOP)
        self.selected_event = tkinter.StringVar()
        event_cb = ttk.Combobox(self, textvariable=self.selected_event)
        self.event_dir = os.path.join(os.path.dirname(__file__),"event")
        event_cb["values"] = [name for name in os.listdir(self.event_dir)\
                              if name !=".DS_Store"]
        event_cb["state"] = "readonly"
        event_cb.pack(side=TOP)
        event_cb.bind("<<ComboboxSelected>>", self.create_form)

    def create_form(self, selected_event):
        result = Toplevel(self)
        topFrame = Frame(result)
        topFrame.pack(side=TOP)
        midFrame = Frame(result)
        midFrame.pack(side=LEFT)
        resultFrame = Frame(result)
        resultFrame.pack(side=LEFT)
        botFrame = Frame(result)
        botFrame.pack(side=RIGHT)
        result.title(self.selected_event.get())

        self.items_list_collection = []
        self.entries_collection = []
        # Fill data from the folder selected
        self.files = sorted([name for name in os.listdir(os.path.join(self.event_dir, self.selected_event.get())) \
                        if name[0].isnumeric() and name.endswith(".csv")])
        for file in files:
            self.items_list_collection.append(pd.read_csv(os.path.join(self.event_dir, self.selected_event.get(), file)))
        df = os.path.join(self.event_dir, self.selected_event.get(), "basic_reward.csv")
        self.basic_reward = (np.loadtxt(open(df), delimiter=","))

        self.bonus_entries = []
        self.items_cost = [0 for _ in range(len(self.files))]

        # Create forms based on the data input
        for i, items_list in enumerate(self.items_list_collection):
            entry = []
            for j, (name, qty) in enumerate(zip(items_list["Name"], items_list["start_qty"])):
                tkinter.Label(topFrame, text=name).grid(row=j, column=i * 2)
                my_entry = Entry(topFrame)
                my_entry.insert(0, qty)
                my_entry.grid(row=j, column=i * 2 + 1)
                entry.append(my_entry)
            self.entries_collection.append(entry)

        for i, name in enumerate(files):
            tkinter.Label(midFrame, text=name[2:-4]).grid(row=i, column=0)
            my_entry = Entry(midFrame)
            my_entry.insert("0", "0")
            my_entry.grid(row=i, column=1)
            self.bonus_entries.append(my_entry)

    def input_value(self,selected_event):
        quiz_name = ["Q9", "Q10", "Q11", "Q12"]
        bnds = [(0, 1000) for _ in range(4)]
        x0 = np.array([1, 1, 1, 1])
        self.items_cost.clear()
        try:
            for list, entries in zip(self.items_list_collection, self.entries_collection):
                item_cost = np.array([int(entry.get()) for entry in entries])
                self.items_cost.append(sum(item_cost * list["Cost"].to_numpy()))
            bonus = np.array([float(entry.get()) for entry in self.bonus_entries])
        except ValueError:
            sys.exit("QTY should be positive integer")
        final_reward = np.ceil(np.array([self.basic_reward[i] * (1 + bonus[i]) for i in range(len(bonus))]))
        cons = [{'type': 'ineq', 'fun': lambda x, coef=i: np.matmul(final_reward[coef], x) - self.items_cost[coef]} for i
                in
                range(len(self.files))]
        sol = minimize(lambda x: sum(x), x0, method='SLSQP', bounds=bnds,
                       constraints=cons)

        for i, name in enumerate(quiz_name):
            tkinter.Label(self, text=name).grid(row=i, column=0)
            tkinter.Label(self, text=np.ceil(sol.x[i])).grid(row=i, column=1)

    my_button = Button(botFrame, text="Input", command=input_value)
    my_button.pack()
        # Setting for scipy minimize



a = calculator()
a.mainloop()