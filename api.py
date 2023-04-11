import sqlite3
import time
import tkinter
import tkinter.ttk
import zoneinfo
from datetime import datetime
from tkinter import *
from sqlite3 import Connection, Cursor
from tkinter import messagebox
from typing import List, Any


def filter_items(connection: Connection, filter_id: str, filter_name: str) -> List[Any]:
    cur = connection.cursor()
    items = cur.execute("SELECT * FROM items WHERE id LIKE ? AND name LIKE ?",
                        (f"%{filter_id}%", f"%{filter_name}%"))
    return items.fetchall()


def add_items(session, connection: Connection, name: str, quantity: str):
    # Clear old messages
    widgets = session.root.pack_slaves()
    for w in widgets:
        if type(w) is tkinter.Label:
            w.destroy()

    message = Label(session.root, text="", font=("Arial", 12))

    # check if quantity is proper:
    if quantity.isnumeric():
        quantity = int(quantity)
        cur = connection.cursor()
        # First we search for grabbing the quantity
        cur.execute("SELECT qty FROM items WHERE name=?", (name,))
        amount = cur.fetchall()

        if not amount:
            # This item doesn't exist we add it
            cur.execute("INSERT INTO items (name, qty) VALUES(?, ?)", (name, quantity))
            message.config(text="Successfully added new entry with {} item(s)".format(quantity))

        else:
            # update the item quantity accordingly
            cur.execute("UPDATE items SET qty=qty+? WHERE name=?", (quantity, name))
            message.config(text="Successfully added {} item(s)".format(quantity))

        connection.commit()

    else:
        message.config(text="Please use a valid (int) quantity")

    message.pack()


def remove_items(session, connection: Connection, name: str, quantity: str):
    # Clear old messages
    widgets = session.root.pack_slaves()
    for w in widgets:
        if type(w) is tkinter.Label:
            w.destroy()

    message = Label(session.root, text="", font=("Arial", 12))

    # check if quantity is proper:
    if quantity.isnumeric():
        quantity = int(quantity)
        cur = connection.cursor()

        # update the item quantity accordingly
        cur.execute("UPDATE items SET qty=qty-? WHERE name=?",
                    (quantity, name))

        # Check to see if qty <= 0
        cur.execute("SELECT qty FROM items WHERE name=?", (name,))
        amount = cur.fetchall()
        # Had to do this weird indexing cause of tuple format
        if amount[0][0] <= 0:
            # Remove entry
            cur.execute("DELETE FROM items WHERE qty<=0 and name=?",
                        (name,))
            messagebox.showinfo("Success", "Successfully removed entry: {} with 0 item(s)".format(name))

        else:
            messagebox.showinfo("Success", "Successfully removed {} item(s)".format(quantity))

        connection.commit()

    else:
        messagebox.showerror("Error", "Please use a valid (int) quantity")

    message.pack()


def log_event(connection: Connection, id: str, user: str, name: str, evt_type: str, qty: int) -> bool:
    """
    Logs events to the events database.

    type should be one of ("In", "Out")

    :param qty:
    :param user:
    :param connection:
    :param id:
    :param name:
    :param evt_type:
    :return:
    """
    date = datetime.utcnow()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO events VALUES(?, ?, ?, ?, ?, ?)", (str(date), user, qty, evt_type, id, name))
        connection.commit()
        return True
    except sqlite3.Error:
        return False
