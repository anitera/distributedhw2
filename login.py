import os
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
	
try:
    import tkMessageBox as tkBox
except ImportError:
    from tkinter import messagebox as tkBox
	
nicknames = []
authorizedNickname = ""

class Nickname:
    ''' correspond for the GUI of nicknames '''
    def __init__(self):
        self.name = ""
        self.passed = False
    
    def setNickname(self, nickname):
        self.name = nickname
        
    def getNickname(self):
        return self.name

def send_data(listbox, nickname_entry, window, nick):
    ''' send an entering data to the client '''
    current = listbox.curselection()
    if current:
        nickname = listbox.get(current[0])
        print("Authorization...", nickname)
    else:
        nickname = nickname_entry.get()
        print("Authorization...", nickname)
    if validate_nickname(nickname):
        if not current:
            with open("client.ini", "a") as cli:
                cli.write(nickname + "\n")			
        nick.passed = True
        nick.setNickname(nickname)
        print("Welcome,", nickname)
        tkBox.showinfo("Successful authorization!", "Authorization passed, try to connect to server")
        window.destroy()
    else:
        print("Authorization doesn't pass")
        tkBox.showinfo("Invalid username!", "try login again")
        nickname_entry.delete(0, len(nickname))
        nickname_entry.insert(0, "")
 
def authorization(users_list, nick):
    ''' GIU window for nicknames '''
    window = tk.Tk()
    listbox_label_location_x = 10
    listbox_label_location_y = 10
    listbox_label_x = 10
    listbox_label_y = 30
    nickname_label_x = 200
    nickname_label_y = 30
    nickname_x = 200
    nickname_y = 60
    button_x = 200
    button_y = 150
    button_height = 4
    button_width = 15
    window.geometry('370x250')
    window.resizable(width=True, height=True)
    window.title('Authorization')
    listbox_text = tk.Label(text = "Choose nickname from list")
    listbox_text.place(x = listbox_label_location_x, y = listbox_label_location_y)
    listbox = tk.Listbox(window)
    users_counter = 0
    users_list = sorted(users_list) # Not neccessary
    for users in set(users_list):
        listbox.insert(users_counter, users)
        users_counter += 1
    listbox.place(x=listbox_label_x, y=listbox_label_y)
    nickname_text = tk.Label(text="OR Enter your nickname")
    nickname_text.place(x=nickname_label_x, y = nickname_label_y)
    nickname = tk.Entry()
    nickname.place(x=nickname_x, y=nickname_y)
    a = tk.Button(window, text=" Authorize ", command=lambda: send_data(listbox, nickname, window, nick))
    a.config(height = button_height, width = button_width)
    a.place(x=button_x, y=button_y)
    window.mainloop()

def validate_nickname(nickname):
    ''' check the lenght of nickname '''
    if len(nickname) == 0 or ' ' in nickname or len(nickname) > 8:
        return False
    else:
        return True
		
def show_nicknames():
    ''' show nicknames in GUI window '''
    for id, nick in enumerate(nicknames):
        print id, nick

def load_nicknames(): 
    ''' load nicknames '''
    if os.path.exists("client.ini"):
        with open("client.ini", "r+") as cli:
            for id, nick in enumerate(cli.readlines()):
                nick = nick[:-1]
                nicknames.append(nick)
        
        show_nicknames()

    if len(nicknames) > 0:
       return True
    else:
        return False

def enter_nickname(load=True):
    ''' authorize a new client with a new name in sudoku '''
    nick = Nickname()
    if load:
	    load_nicknames()
    authorization(nicknames, nick)
    return nick.getNickname()



