import sqlite3
import tkinter
import tkinter.ttk
from tkinter import *
from sqlite3 import Connection, Cursor
from typing import List, Any
import datetime


def filter_items(connection: Connection, filter_id: str, filter_name: str) -> List[Any]:
    cur = connection.cursor()
    items = cur.execute("SELECT * FROM items WHERE id LIKE ? AND name LIKE ?",
                        (f"%{filter_id}%", f"%{filter_name}%"))
    return items.fetchall()


def get_item(connection: Connection, filter_id: str) -> Any:
    cur = connection.cursor()
    item = cur.execute("SELECT * FROM items WHERE id IS ?", (filter_id,))
    return item.fetchone()


def get_item_by_name(connection: Connection, filter_name: str) -> Any:
    cur = connection.cursor()
    item = cur.execute("SELECT * FROM items WHERE name IS ?", (filter_name,))
    return item.fetchone()


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


def insert_event(connection: Connection, user_id, qty: str, type, item_id: str, item_name: str) -> bool:
    """
    Logs event into event table
    type must be one of ("In", "Out")

    Returns True if write is successful, False otherwise

    :param connection:
    :param user_id:
    :param qty:
    :param type:
    :param item_id:
    :param item_name:
    :return:
    """
    cursor = connection.cursor()
    dt = datetime.datetime.now()
    cursor.execute("INSERT INTO events VALUES(?, ?, ?, ?, ?, ?)", (str(dt), user_id, qty, type, item_id, item_name))
    connection.commit()
    try:

        return True
    except sqlite3.Error:
        return False
