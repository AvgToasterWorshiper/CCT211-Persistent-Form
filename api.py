import sqlite3
import tkinter.ttk
from sqlite3 import Connection, Cursor
from typing import List, Any


def filter_items(connection: Connection, filter_id: str, filter_name: str) -> List[Any]:
    cur = connection.cursor()
    items = cur.execute("SELECT * FROM items WHERE id LIKE ? AND name LIKE ?",
                        (f"%{filter_id}%", f"%{filter_name}%"))
    return items.fetchall()


def update_items(treeview: tkinter.ttk.Treeview, connection: Connection, filter_id: str, filter_name: str) -> None:
    for row in treeview.get_children():
        treeview.delete(row)

    items = filter_items(connection, filter_id, filter_name)
    for item in items:
        treeview.insert("", 0, values=(item[0], item[1], item[2]))
