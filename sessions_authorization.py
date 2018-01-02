import os
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
	
try:
    import tkMessageBox as tkBox
except ImportError:
    from tkinter import messagebox as tkBox

sessionname_return = ''
sessuionsize_return = 0


def send_data_sessions(listbox, sessions, number_of_players, window): 
    print 'send data ', listbox, ' sess: ', sessions
    current = listbox.curselection()
    global sessionname_return
    global sessionsize_return
    if current:
        print 'Decide to join existing session'
        sessionname = listbox.get(current[0])
        print("Session size is...", sessionname)
        window.destroy()
        sessionname_return = sessionname[1]
        sessionsize_return = sessionname[0]
	
    else:
        sessionname = sessions.get()
        sessionsize = number_of_players.get()
        print("Connecting to...", sessionname)
	#return session_size
        if validate_session_name_and_size(sessionname, sessionsize):
            print("Welcome,", sessionname)
            tkBox.showinfo("Connected!", "Have fun!")
            window.destroy()
            sessionname_return = sessionname
            sessionsize_return = sessionsize
        else:
            print("CAN NOT CONNECT TO SESSION")
            tkBox.showinfo("Session already booked", "try another session")
            sessions.delete(0, len(sessionname))
            sessions.insert(0, "")        


def validate_session_name_and_size(session_name, session_size):
    if len(session_name) == 0 or ' ' in session_name or len(session_name) > 8 or session_size == 0 or isinstance( session_size, ( int, long ) ):
        return False
    else:
        return True



    
def sessionStart(sessions):
    window = tk.Tk()

    listbox_label_location_x = 10
    listbox_label_location_y = 10
    listbox_label_x = 10
    listbox_label_y = 30

    session_label_x = 200
    session_label_y = 30
    session_x = 200
    session_y = 60

    number_label_x = 200
    number_label_y = 80
    number_x = 200
    number_y = 120

    button_x = 200
    button_y = 150
    button_height = 4
    button_width = 15

    window.geometry('370x250')
    window.resizable(width=True, height=True)
    window.title('Sessions')
    listbox_text = tk.Label(text = "Join exesting session")
    listbox_text.place(x = listbox_label_location_x, y = listbox_label_location_y)
    listbox = tk.Listbox(window)

    sessions_counter = 0
    #sessions_list = sorted(sessions_list) # Not neccessary
    for sess in sessions:
        listbox.insert(sessions_counter, sess)
        sessions_counter += 1
    listbox.place(x=listbox_label_x, y=listbox_label_y)
    session_text = tk.Label(text="Create new one. \n Enter session name:")
    session_text.place(x=session_label_x, y = session_label_y)

    session = tk.Entry()
    session.place(x=session_x, y=session_y)

    number_label = tk.Label(text="Create new one. \n Enter number of players:")
    number_label.place(x = number_label_x, y = number_label_y)

    number_of_players = tk.Entry()
    number_of_players.place(x=number_x, y=number_y)

    a = tk.Button(window, text="Pick session", command=lambda: send_data_sessions(listbox, session, number_of_players, window))
    a.config(height = button_height, width = button_width)
    a.place(x=button_x, y=button_y)
    window.mainloop()
    global sessionname_return
    global sessionsize_return
    return (sessionname_return, sessionsize_return)

'''
def show_sessions():
    for id, sess in enumerate(sessions_list):
        print id, sess

def load_sessions(sessions_list, sessions_size): 
    content = (sessions_list, sessions_size)
    print content
    show_sessions()

    if len(sessions_list) > 0:
        for id, sess in enumerate(sessions_list):
        print id, sess
        return True
    else:
	print 'There are no sessions yet, please create new'
        return False

def sessionStart(sessions, load=True):
    #session_chosen = Session_Authorization()
    print 'session_chosen', sessions
    if load:
        load_sessions()
    sessionsAuthorization(sessions_list, sessions)
    return session_chosen.getSessionId()

'''

if __name__== "__main__":
    sessions = [('ses1', 5), ('ses2', 6), ('ses3', 7)]
    s_ret = sessionStart(sessions)
    print 'Size of session', s_ret[0]
    print 'Session name ', s_ret[1]


