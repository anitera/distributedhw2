try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
	
try:
    import tkMessageBox as tkBox
except ImportError:
    from tkinter import messagebox as tkBox

class HostPort:
    def __init__(self):
        self.host = ""
        self.port = ""
    
    def setHostPort(self, hostport):
        self.host = hostport[0]
        self.port = hostport[1]
        
    def getHostPort(self):
        return (self.host, self.port)

def sendPortHost(hostport_entry, window, hp):
    hostport_data = hostport_entry.get().split(":")
    if len(hostport_data) == 2 and hostport_data[1].isdigit():
        tkBox.showinfo("Checking host and port", "Please, wait...")
        hp.setHostPort(hostport_data)
        window.destroy()
    else:
        tkBox.showinfo("Checking host and port", "Incorrect format of host:port")
        window.destroy()
    
def hostPortAuthorization(HP):
    window = tk.Tk()
    nickname_label_x = 85
    nickname_label_y = 30
    nickname_x = 52
    nickname_y = 60
    button_x = 60
    button_y = 90
    button_height = 3
    button_width = 15
    window.geometry('265x150')
    window.resizable(width=False, height=False)
    window.title('Host - port authorization')
    hostPortText = tk.Label(text="Enter host:port")
    hostPortText.place(x=nickname_label_x, y = nickname_label_y)
    hostPort = tk.Entry()
    hostPort.place(x=nickname_x, y=nickname_y)
    b = tk.Button(window, text="Authorize", command=lambda: sendPortHost(hostPort, window, HP))
    b.config(height = button_height, width = button_width)
    b.place(x=button_x, y=button_y)
    window.mainloop()