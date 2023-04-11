import tkinter
from sqlite3 import Connection
from tkinter import *
from tkinter import messagebox, ttk
import sqlite3

import api


class Session:
    def __init__(self, root, userID=None):
        self.current_user = userID
        self.root = root
        self.connection = sqlite3.connect("./Persistent Inventory Management System.db")
        self.attempt_user = StringVar()
        self.attempt_pass = StringVar()

        self.perms = {}

    def logout(self):
        self.current_user = None
        self.perms = {}

        create_menus(self)

    def update_items(self, treeview: tkinter.ttk.Treeview, connection: Connection, filter_id: str, filter_name: str):
        for row in treeview.get_children():
            treeview.delete(row)

        items = api.filter_items(connection, filter_id, filter_name)
        for item in items:
            treeview.insert("", 0, values=(item[0], item[1], item[2]))

    def update_qty(self, item_id: str, query_type: str, event_type: str, qty: str):
        item = None
        if query_type == "id":
            item = api.get_item(self.connection, item_id)
        else:
            item = api.get_item_by_name(self.connection, item_id)

        if int(qty) <= 0:
            messagebox.showerror("Invalid Quantity", "Negative or zero quantity not permitted.")
            return
        if item is None:
            messagebox.showerror("Item Not Found", "That item doesn't exist.\nPlease verify the item ID and try again")
            return
        elif item[2] < int(qty) and event_type.lower() == "out":
            messagebox.showerror("Invalid Quantity", "Sign out request is larger than current quantity.")
            return

        if event_type.lower() == "out":
            if not api.remove_items(self.connection, item[1], qty):
                messagebox.showerror("Write Failed", "An unexpected error occurred.\n"
                                                     "Please try again later.")
                return

        elif event_type.lower() == "in":
            if not api.add_items(self.connection, item[1], qty):
                messagebox.showerror("Write Failed", "An unexpected error occurred.\n"
                                                     "Please try again later.")
                return

        if not api.insert_event(self.connection, self.current_user, qty, event_type, item_id, item[1]):
            messagebox.showerror("Event Log Failed", "Failed to write log.")
        else:
            messagebox.showinfo("Success", f"Successfully signed {event_type.lower()} {qty} item(s).")



    def add_items(self, treeview: tkinter.ttk.Treeview, connection: Connection, name: str, quantity: str) -> None:
        # Will add quantity to {item} or create a new entry if none exist

        # Clear old messages
        widgets = self.root.pack_slaves()
        for w in widgets:
            if type(w) is tkinter.Label:
                w.destroy()

        message = Label(self.root, text="", font=("Arial", 12))

        status = api.add_items(connection, name, quantity)
        if status == 1:
            message.config(
                text="Successfully added new entry with {} item(s)".format(
                    quantity))
        elif status == 2:
            message.config(
                text="Successfully added new entry with {} item(s)".format(
                    quantity))
        elif status == 0:
            message.config(
                text="Please use a valid (int) quantity".format(quantity))

        self.update_items(treeview, connection, '', name)

        message.pack()

    def remove_items(self, treeview: tkinter.ttk.Treeview, connection: Connection, name: str, quantity: str) -> None:
        # Will remove quantity from {item} or remove entry if none exists

        # Clear old messages
        widgets = self.root.pack_slaves()
        for w in widgets:
            if type(w) is tkinter.Label:
                w.destroy()

        message = Label(self.root, text="", font=("Arial", 12))

        status = api.remove_items(connection, name, quantity)
        if status == 1:
            message.config(text="Successfully removed entry: {} with 0 item(s)".format(name))
        elif status == 2:
            message.config(text="Successfully removed {} item(s)".format(quantity))
        elif status == 0:
            message.config(text="Please use a valid (int) quantity")
        elif status == -1:
            message.config(text="{} does not exist in the DB".format(name))

        self.update_items(treeview, connection, '', name)

        message.pack()


def quit(inst):
    inst.root.quit()


def login(inst):
    """
    Check to see if user from entry exits, if so login and switch to new instance

    This function should always reference a logged-out instance
    :param inst:
    :return:
    """
    if inst.current_user is None:
        cur = inst.connection.cursor()
        user = cur.execute("SELECT UserPassword FROM Users WHERE UserID IS ?", (inst.attempt_user.get(),))
        password_fetch = user.fetchone()
        password = None
        if password_fetch is not None:
            password = password_fetch[0]

        if inst.attempt_pass.get() == password:
            inst.current_user = cur.execute("SELECT UserID FROM Users WHERE UserID IS ?",
                                            (inst.attempt_user.get(),)).fetchone()[0]

            # Get Permissions
            inst.perms['View'] = \
                cur.execute("SELECT View FROM Users WHERE UserID IS ?",
                        (inst.attempt_user.get(),)).fetchone()[0]
            inst.perms['Signout'] = \
            cur.execute("SELECT Signout FROM Users WHERE UserID IS ?",
                        (inst.attempt_user.get(),)).fetchone()[0]
            inst.perms['Events'] = \
            cur.execute("SELECT Events FROM Users WHERE UserID IS ?",
                        (inst.attempt_user.get(),)).fetchone()[0]
            inst.perms['AddRemove'] = \
                cur.execute("SELECT AddRemove FROM Users WHERE UserID IS ?",
                            (inst.attempt_user.get(),)).fetchone()[0]

            inst.attempt_user.set("")
            inst.attempt_pass.set("")

            # Call new menu creation
            create_menus(inst)

        else:
            messagebox.showerror(title="Login Failed", message="Incorrect username and/or password.")


def clear_widgets(inst):
    # Clear Inst Widgets
    widgets = inst.root.pack_slaves()
    for w in widgets:
        w.destroy()


def create_menus(inst):
    # Clear Screen
    clear_widgets(inst)

    top = Menu(inst.root)
    root.config(menu=top)

    # Add user tab
    user = Menu(top, tearoff=False)
    user.add_separator()

    if inst.current_user is not None:
        # Logged in user features:

        user.add_command(label='Logout', command= lambda: inst.logout(), underline=0)
        user.add_command(label='Quit', command=lambda: quit(inst), underline=0)
        top.add_cascade(label='User', menu=user, underline=0)

        if inst.perms['View'] == 1:
            # Add Database view tab
            view_inventory = Menu(top, tearoff=False)
            view_inventory.add_separator()
            # TODO: This might not be right, will have to verify later.
            top.add_command(label='View Inventory', command=lambda: create_viewpage(inst))

        if inst.perms['Signout'] == 1:
            # Add Database edit tab
            edit_inventory = Menu(top, tearoff=False)
            edit_inventory.add_command(label="Sign item in/out...", command=lambda: create_signoutpage(inst))
            if inst.perms['AddRemove'] == 1:

                edit_inventory.add_command(label="Add item(s)", command=lambda: create_addpage(inst))
                edit_inventory.add_command(label="Remove item(s)", command=lambda: create_removepage(inst))

            top.add_cascade(label='Edit Inventory', menu=edit_inventory, underline=0)



        if inst.perms['Events'] == 1:
            # Add Database edit tab
            view_events = Menu(top, tearoff=False)
            view_events.add_separator()
            top.add_cascade(label='View Events', menu=view_events, underline=0)

        create_welcomescreen(inst)

    else:
        create_loginpage(inst, user, top)


def create_welcomescreen(inst):
    # Creates welcome page with UserID
    welcome_screen = Frame(inst.root)
    welcome_message = Label(welcome_screen,
                            text='Welcome, {}'.format(inst.current_user),
                            font=("Arial", 15))
    welcome_message.pack(anchor="center", fill=BOTH, expand=1, padx=40, pady=40)
    welcome_screen.pack(anchor="center", fill=BOTH, expand=1, padx=40, pady=40)


def create_loginpage(inst, user, top):
    # This is an 'empty instance'

    login_label = Label(inst.root, text="Please Login To Continue",
                        relief=RAISED, font=("Arial", 25))
    login_label.pack(side='top', fill=BOTH, expand=1)

    login_frame = Frame(inst.root)

    login_frame_left = Frame(login_frame)
    login_userid = Label(login_frame_left, text="Please Enter User ID: ",
                         font=("Arial", 12))
    login_userpassword = Label(login_frame_left,
                               text="Please Enter User Password: ",
                               font=("Arial", 12))
    login_userid.pack(side='top', fill=BOTH, expand=1)
    login_userpassword.pack(side='top', fill=BOTH, expand=1)

    login_frame_right = Frame(login_frame)
    userid_entry = Entry(login_frame_right, font=("Arial", 12),
                         textvariable=inst.attempt_user)
    userpassword_entry = Entry(login_frame_right, font=("Arial", 12), show="*",
                               textvariable=inst.attempt_pass)
    userid_entry.pack(side='top', fill=BOTH, expand=1, padx=40, pady=40)
    userpassword_entry.pack(side='top', fill=BOTH, expand=1, padx=40, pady=40)

    userid_entry.bind('<Return>', lambda event: login(inst))
    userpassword_entry.bind('<Return>', lambda event: login(inst))

    login_frame_left.pack(side='left', fill=BOTH, expand=1)
    login_frame_right.pack(side='right', fill=BOTH, expand=1)

    login_frame.pack(side='top', fill=BOTH, expand=1)

    login_button = Button(inst.root, command=lambda: login(inst),
                          text="Login", font=("Arial", 15))
    login_button.pack(side='top', fill=BOTH, expand=1, padx=40, pady=40)

    user.add_command(label='Quit', command=lambda: quit(inst), underline=0)
    top.add_cascade(label='User', menu=user, underline=0)


def create_viewpage(inst):
    # Clear Screen
    clear_widgets(inst)

    view = ttk.Treeview(inst.root, columns=("id", "name", "qty"))
    inst.update_items(view, inst.connection, "", "")
    view.heading("id", text="Item ID")
    view.heading("name", text="Name")
    view.heading("qty", text="Quantity")

    filter_frame = LabelFrame(inst.root, text="Filter Items")
    id_frame = Frame(filter_frame)
    id_label = Label(id_frame, text="Item ID:")
    id_entry = Entry(id_frame)

    id_label.pack(side='left')
    id_entry.pack(side='left')

    name_frame = Frame(filter_frame)
    name_label = Label(name_frame, text="Item Name:")
    name_entry = Entry(name_frame)

    enter_button = Button(filter_frame, text="Filter",
                          command=lambda: inst.update_items(view, inst.connection, id_entry.get(), name_entry.get()))

    name_label.pack(side='left')
    name_entry.pack(side='left')

    id_frame.pack()
    name_frame.pack()
    enter_button.pack()

    filter_frame.pack()
    view.pack()


def create_addpage(inst):
    # Clear Screen
    clear_widgets(inst)

    view = ttk.Treeview(inst.root, columns=("id", "name", "qty"))
    inst.update_items(view, inst.connection, "", "")
    view.heading("id", text="Item ID")
    view.heading("name", text="Name")
    view.heading("qty", text="Quantity")

    filter_frame = LabelFrame(inst.root, text="Enter Item Name and Quantity to Add")

    name_frame = Frame(filter_frame)
    name_label = Label(name_frame, text="Item Name:")
    name_entry = Entry(name_frame)

    name_label.pack(side='left')
    name_entry.pack(side='left')

    quantity_frame = Frame(filter_frame)
    quantity_label = Label(quantity_frame, text="Quantity:")
    quantity_entry = Entry(quantity_frame)

    quantity_label.pack(side='left')
    quantity_entry.pack(side='left')

    enter_button = Button(filter_frame, text="Add Item(s)",
                          command=lambda: inst.add_items(view,
                                                            inst.connection,
                                                            name_entry.get(), quantity_entry.get()))



    name_frame.pack()
    quantity_frame.pack()
    enter_button.pack()

    filter_frame.pack()
    view.pack()

def create_removepage(inst):
    # Clear Screen
    clear_widgets(inst)

    view = ttk.Treeview(inst.root, columns=("id", "name", "qty"))
    inst.update_items(view, inst.connection, "", "")
    view.heading("id", text="Item ID")
    view.heading("name", text="Name")
    view.heading("qty", text="Quantity")

    filter_frame = LabelFrame(inst.root,
                              text="Enter Item Name and Quantity to Remove")

    name_frame = Frame(filter_frame)
    name_label = Label(name_frame, text="Item Name:")
    name_entry = Entry(name_frame)

    name_label.pack(side='left')
    name_entry.pack(side='left')

    quantity_frame = Frame(filter_frame)
    quantity_label = Label(quantity_frame, text="Quantity:")
    quantity_entry = Entry(quantity_frame)

    quantity_label.pack(side='left')
    quantity_entry.pack(side='left')

    enter_button = Button(filter_frame, text="Remove Item(s)",
                          command=lambda: inst.remove_items(view,
                                                         inst.connection,
                                                         name_entry.get(),
                                                         quantity_entry.get()))

    name_frame.pack()
    quantity_frame.pack()
    enter_button.pack()

    filter_frame.pack()
    view.pack()

def create_eventspage(root):
    pass


def create_signoutpage(inst: Session):
    clear_widgets(inst)
    query_type = StringVar(inst.root, "id")
    item_query = StringVar()

    item_frame = LabelFrame(inst.root, text="Item to modify")

    Label(item_frame, text="Search item").pack()
    item_search_frame = Frame(item_frame)

    Entry(item_search_frame, textvariable=item_query).pack()
    item_type_frame = Frame(item_search_frame)

    Label(item_type_frame, text="Search by: ").pack(side='left')
    Radiobutton(item_type_frame, text="ID", variable=query_type, value="id").pack(side='left')
    Radiobutton(item_type_frame, text="Item Name", variable=query_type, value="name").pack(side='left')

    item_search_frame.pack()
    item_type_frame.pack()
    item_frame.pack()

    qty_frame = Frame(inst.root)
    qty = StringVar(inst.root, "1")

    Label(qty_frame, text="Quantity: ").pack(side='left')
    Entry(qty_frame, textvariable=qty).pack(side='left')
    qty_frame.pack()
    sign = StringVar(inst.root, "out")
    Radiobutton(inst.root, text="In", variable=sign, value="in").pack()
    Radiobutton(inst.root, text="Out", variable=sign, value="out").pack()

    Button(inst.root, text="Submit", command=lambda: inst.update_qty(item_query.get(), query_type.get(), sign.get(),
                                                                     qty.get())).pack()


# Initialize tk
root = Tk()
root.title('Persistent Inventory Management System')
root.geometry("800x600")

# App instance, by default instance is a 'logged out instance'
instance = Session(root)

# Create app menus appropriate to that instance (loggin'd in user)
create_menus(instance)


root.mainloop()
