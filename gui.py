# Authored By- Akash Kumar Bhagat
# Github Id - @charlie219
# Email - akashkbhagat221199@gmail.com
# Date - 24-6-2021


import tkinter as tk
from tkinter import *
from engine import Client
from tkinter import messagebox
from PIL import Image,ImageTk

class Application:
    def __init__(self, usr_name = None):
        self.window_width = 500
        self.window_height = 500
        self.root = tk.Tk()
        self.bg_color = "#cc66ff"
        canvas = tk.Canvas(self.root, height = self.window_height, width = self.window_width)
        canvas.pack()

        self.main_frame = tk.Frame(self.root, bg = self.bg_color)
        self.main_frame.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.9)
        
        def top_frame_widget():
            app_lable1 = tk.Label(self.main_frame, text = "𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮", bg = "#dd99ff",  font = ('Times New Roman',34))
            app_lable2 = tk.Label(self.main_frame, text = "𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟", bg = "#dd99ff",  font = ('Times New Roman',18))
            
            app_lable1.place(relx = 0.2, rely = 0.02, relheight = 0.15, relwidth = 0.6)
            app_lable2.place(relx = 0.2, rely = 0.15, relheight = 0.1, relwidth = 0.6)


        self.name = 0
        self.user_name = 0
        top_frame_widget()
        if usr_name == None:
            self.index()
        else:
            self.choice(usr_name, chk_point = 1)
        self.root.mainloop()
        
    
    def index(self, prev_frame = None):

        # Destroy Previous Frame
        if prev_frame:
            prev_frame.destroy()

        self.root.title('Enter User Name')

        # Creating a new Frame
        frame = tk.Frame(self.main_frame,bg = self.bg_color)
        frame.place(relx = 0, rely = 0.3, relheight = 0.7, relwidth = 1)
        
        avatar_img = PhotoImage(file = 'images/avatar.png')
        avatar_label = tk.Label(frame, image = avatar_img)
        avatar_label.place(relx = 0.31, rely = 0, relheight = 0.54, relwidth = 0.38)

        entry = tk.Entry(frame, font = ('Times New Roman', 13))
        entry.insert(0,'User Name')
        entry.configure(state=DISABLED)

        # For Placeholder in the entry tag
        def on_click(event):
            entry.configure(state=NORMAL)
            entry.delete(0, END)
            entry.unbind('<Button-1>', on_click_id)

        # Check for validity
        def chk(uname):
            if uname == 'User Name' or uname == '':
                return False
            
            return True

        def required_field():
            messagebox.showerror("Required Field", "Please enter a User Name to enter")

        on_click_id = entry.bind('<Button-1>', on_click)
        entry.place(relx = 0.33 , rely = 0.60, relwidth = 0.34, relheight = 0.09)

        submit_button = tk.Button(frame, bd = 5, fg = "white", bg = "#550080", text = "GO >>", font = ("serif bold", 13),\
                activebackground = "#dd99ff", activeforeground = "black", \
                command = lambda : self.choice(entry.get(), prev_frame = frame) if chk(entry.get()) else required_field())
        submit_button.place(relx = 0.4, rely = 0.72, relwidth = 0.20, relheight = 0.1)

        self.root.mainloop()

    def choice(self, uname, prev_frame = None, chk_point = 0):
        # Destroy Previous Frame
        if prev_frame:
            prev_frame.destroy()

        # Creating a new Frame
        frame = tk.Frame(self.main_frame,bg = self.bg_color)
        frame.place(relx = 0, rely = 0.3, relheight = 0.7, relwidth = 1)
        self.user_name = uname
        
        self.root.title('Make your Choice')
        

        create_img = Image.open('images/create.jpg')
        create_img = ImageTk.PhotoImage(create_img.resize((120, 120)))
        create_label = Label(frame, image = create_img)
        create_label.place(relx = 0.1, rely = 0.08, relheight = 0.38, relwidth = 0.27)

        create_button = tk.Button(frame,  bd = 5, fg = "white", bg = "#006600", text = "Create Group", font = ("serif bold", 13),\
                activebackground = "#00e673", activeforeground = "black", command = lambda: Client(self.user_name, 1, previousFrame = self.root))
        create_button.place(relx = 0.105, rely = 0.5, relwidth = 0.26, relheight = 0.1)

        join_img = Image.open('images/join.png')
        join_img = ImageTk.PhotoImage(join_img.resize((120, 120)))
        join_label = Label(frame, image = join_img)
        join_label.place(relx = 0.63, rely = 0.08, relheight = 0.38, relwidth = 0.27)

        def enter_group_id():
            entry = tk.Entry(frame, font = ('Times New Roman', 13))
            entry.insert(0, 'Group ID')
            entry.configure(state = DISABLED)
            entry.place(relx = 0.6 , rely = 0.65, relwidth = 0.20, relheight = 0.09)

            # For Placeholder in the entry tag
            def on_click(event):
                entry.configure(state = NORMAL)
                entry.delete(0, END)
                entry.unbind('<Button-1>', on_click_id)
            
            # Check for validity
            def chk(group_id):
                if group_id == 'Group ID' or group_id == '':
                    return False
            
                return True

            def required_field():
                messagebox.showerror("Required Field", "Please enter a Group ID to enter")
            
            on_click_id = entry.bind('<Button-1>', on_click)
            entry.place(relx = 0.6 , rely = 0.65, relwidth = 0.20, relheight = 0.09)

            submit_button = tk.Button(frame, bd = 5, fg = "white", bg = "#550080", text = "GO >>", font = ("serif bold", 13),\
                activebackground = "#dd99ff", activeforeground = "black", \
                command = lambda : Client(self.user_name, 2, group_id = entry.get(), previousFrame = self.root) if chk(entry.get()) else required_field())
            submit_button.place(relx = 0.82, rely = 0.645, relwidth = 0.15, relheight = 0.1)


        join_button = tk.Button(frame,  bd = 5, fg = "white", bg = "#804000", text = "Join Group", font = ("serif bold", 13),\
                activebackground = "#ff9933", activeforeground = "black", command = lambda: enter_group_id())
        join_button.place(relx = 0.66, rely = 0.5, relwidth = 0.21, relheight = 0.1)

        back_button = tk.Button(frame,  bd = 5, fg = "white", bg = "#550080", text = "<< BACK", font = ("serif bold", 13),\
                activebackground = "#dd99ff", activeforeground = "black", command = lambda: self.index(frame))
        back_button.place(relx = 0.4, rely = 0.8, relwidth = 0.20, relheight = 0.1)

        if chk_point:        messagebox.showerror("Incorrect Group ID", "Enter Group ID doesn't Exist")

        self.root.mainloop()

# root = tk.Tk()
# app = Application(root)
