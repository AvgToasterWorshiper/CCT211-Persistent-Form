import sqlite3
import tkinter
import tkinter.ttk
from tkinter import *
from sqlite3 import Connection, Cursor
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

    #check if quantity is proper:
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
