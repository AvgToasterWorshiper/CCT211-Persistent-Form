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

        self.perms = {'View': 0, 'Edit': 0, 'Events': 0}

    def logout(self):
        self.current_user = None
        self.perms = {'View': 0, 'Edit': 0, 'Events': 0}

        create_menus(self)

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
            inst.perms['Edit'] = \
            cur.execute("SELECT Edit FROM Users WHERE UserID IS ?",
                        (inst.attempt_user.get(),)).fetchone()[0]
            inst.perms['Events'] = \
            cur.execute("SELECT Events FROM Users WHERE UserID IS ?",
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

        if inst.perms['Edit'] == 1:
            # Add Database edit tab
            edit_inventory = Menu(top, tearoff=False)
            edit_inventory.add_separator()
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
    api.update_items(view, inst.connection, "", "")
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
                          command=lambda: api.update_items(view, inst.connection, id_entry.get(), name_entry.get()))

    name_label.pack(side='left')
    name_entry.pack(side='left')

    id_frame.pack()
    name_frame.pack()
    enter_button.pack()

    filter_frame.pack()
    view.pack()


def create_editpage(root):
    pass

def create_eventspage(root):
    pass

# Initialize tk
root = Tk()
root.title('Persistent Inventory Management System')
root.geometry("800x600")

# App instance, by default instance is a 'logged out instance'
instance = Session(root)

# Create app menus appropriate to that instance (loggin'd in user)
create_menus(instance)


root.mainloop()
