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

def add_items(connection: Connection, name: str, quantity: str) -> int:

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

            connection.commit()
            return 2

        else:
            # update the item quantity accordingly
            cur.execute("UPDATE items SET qty=qty+? WHERE name=?", (quantity, name))

            connection.commit()
            return 1
    else:
        return 0

def remove_items(connection: Connection, name: str, quantity: str) -> int:
    # check if quantity is proper:
    if quantity.isnumeric():
        quantity = int(quantity)
        cur = connection.cursor()

        # check if name exists in DB
        cur.execute("SELECT * FROM items WHERE name=?", (name,))
        name = cur.fetchall()
        if not name:
            return -1

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
            connection.commit()
            return 1

        else:

            connection.commit()
            return 2

    else:
        return 0
