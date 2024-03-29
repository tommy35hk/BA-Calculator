import csv
import numpy as np
import tkinter
from scipy.optimize import minimize
from tkinter import *
from tkinter import ttk
import os

root = Tk()
root.title("BA Calculator")
root.resizable(False, False)

items_cost = []
final_reward = None

"""
Create the first page for selecting events
"""


class EventSelection:
    def __init__(self, master):
        my_frame = Frame(master)
        my_frame.pack()
        label = ttk.Label(my_frame, text="Please select an event:")
        label.pack(side=TOP)
        self.selected_event = tkinter.StringVar()
        event_cb = ttk.Combobox(master, textvariable=self.selected_event)

        self.event_dir = os.path.join(os.path.dirname(__file__), "event")
        event_cb["values"] = [
            name for name in os.listdir(self.event_dir)
            if name != ".DS_Store"
        ]
        event_cb["state"] = "readonly"
        event_cb.pack(side=TOP)

        event_cb.bind("<<ComboboxSelected>>", self.create_form)

    def create_form(self, *args):
        EventFrame(self.event_dir, self.selected_event.get())


"""
Class for collecting items qty that needed
"""


class ItemEntry:
    def __init__(self, master, event_dir, csvfile):
        global items_cost
        my_frame = Frame(master)
        my_frame.pack(side=LEFT)
        self.entries = []
        self.item_cost = []
        Label(my_frame, text=csvfile[2:-4]).grid(row=0, column=0, columnspan=2)
        with open(os.path.join(event_dir, csvfile), "r") as f:
            reader = csv.DictReader(f)
            for i, line in enumerate(reader):
                Label(my_frame, text=line["Name"]).grid(row=i + 1, column=0)
                my_entry = Entry(my_frame)
                my_entry.insert(0, line["start_qty"])
                my_entry.grid(row=i + 1, column=1)
                self.entries.append(my_entry)
                self.item_cost.append(int(line["Cost"]))

    def count(self):
        self.item_qyy = np.array([int(entry.get()) for entry in self.entries])
        self.item_cost = np.array(self.item_cost)
        items_cost.append(sum(self.item_cost * self.item_qyy))


"""
Class for collecting the reward bonus
"""


class BonusEntry:

    def __init__(self, master, csvfile, files):
        my_frame = Frame(master)
        my_frame.pack(side=LEFT)
        self.bonus_entries = []

        for i, name in enumerate(files):
            Label(my_frame, text=name[2:-4]).grid(row=i, column=0)
            my_entry = Entry(my_frame)
            my_entry.insert("0", "0")
            my_entry.grid(row=i, column=1)
            self.bonus_entries.append(my_entry)
        with open(csvfile) as f:
            reader = f.readlines()
            self.reward = np.loadtxt(reader[1:], delimiter=",")

    def count(self):
        global final_reward
        self.bonus = np.array([float(entry.get()) for entry in self.bonus_entries])
        self.reward = np.array(self.reward)
        final_reward = np.array([(1 + self.bonus[i]) * self.reward[i] for i in range(len(self.bonus_entries))])
        final_reward = np.ceil(final_reward)


class EventFrame:
    def __init__(self, event_dir, selected_event):
        self.result = Toplevel(root)
        self.items_frame = Frame(self.result)
        self.items_frame.pack(side=TOP)
        self.bottom_frame = Frame(self.result)
        self.bottom_frame.pack(side=LEFT)
        self.button_frame = Frame(self.result)
        self.button_frame.pack(side=RIGHT)
        self.event_dir = event_dir
        self.selected_event = selected_event

        target_dir = os.path.join(self.event_dir, self.selected_event)
        files = sorted([
            name for name in os.listdir(target_dir)
            if name[0].isnumeric() and name.endswith(".csv")
        ])
        events = [
            ItemEntry(self.items_frame, target_dir, file)
            for file in files
        ]
        df = os.path.join(target_dir, "basic_reward.csv")
        with open(df) as f:
            reader = f.readlines()
            self.mission = reader[0].strip().split(",")
        bonus = BonusEntry(self.bottom_frame, df, files)
        self.result_frame = Frame(self.bottom_frame)
        self.result_frame.pack(side=LEFT)
        my_button = Button(
            self.button_frame, text="Count",
            command=lambda: [
                items_cost.clear(),
                [event.count() for event in events],
                bonus.count(),
                self.count_minimum(items_cost, final_reward)
            ]
        )
        my_button.pack()

    def count_minimum(self, items_cost, final_reward):
        bnds = [(0, 10000) for _ in range(len(self.mission))]
        x0 = np.array([1 for _ in range(len(self.mission))])
        cons = [
            {
                'type': 'ineq',
                'fun': lambda x, coef=i: np.matmul(final_reward[coef], x) - items_cost[coef]
            } for i in range(len(final_reward))
        ]
        sol = minimize(lambda x: sum(x), x0, method="SLSQP", bounds=bnds, constraints=cons)
        for i, name in enumerate(self.mission):
            Label(self.result_frame, text=name).grid(row=i, column=0)
            Label(self.result_frame, text=np.ceil(sol.x[i])).grid(row=i, column=1)


EventSelection(root)
root.mainloop()
