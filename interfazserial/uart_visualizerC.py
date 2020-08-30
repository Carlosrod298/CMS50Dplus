"""This is a simple application written in Python and TKinter.
The application's main purpose is not to serve a specific one. This is a generic application
for sending and receiving data from the computer to UART host controller.
The major functions are self update and get data which are threaded to make sure the GUI does not freeze.
The GUI runs in the main thread, the worker threads are the two separate ones.
A simple CMS50D+ is also made to test the purpose of this app which sends data in a specific

Please install first:

- sudo apt install python3-pip
- pip3 install pyserial

Run the script

"""

# Import  libraries
import time
import threading
import sys


if sys.version_info[0] < 3:
    #If we're executing with Python 2
    import Tkinter as tk
    import tkMessageBox as messagebox
    import ttk
    import tkFileDialog as filedialog
    import tkColorChooser as colorchooser
else:
    #Otherwise we're using Python 3
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import colorchooser




import serial


from interfazserial import SerialFCnCms

serial_data = ''
Sp02  =''
PRbmp =''
dataInStr = ''
filter_data = [0,0]
statePort = False  # flag to detect when the thread is  listening  port serial

update_period = 4
serial_object = serial.Serial()
gui = tk.Tk()
gui.title("UART Interface")

baudlist = [4800, 9600, 19200, 38400, 57600, 115200, 230400, 921600]


def connect():
    """The function initiates the Connection to the UART device with the Port and Buad fed through the Entry
    boxes in the application.
    The radio button selects the platform, as the serial object has different key phrases
    for Linux and Windows. Some Exceptions have been made to prevent the app from crashing,
    such as blank entry fields and value errors, this is due to the state-less-ness of the
    UART device, the device sends data at regular intervals irrespective of the master's state.
    The other Parts are self explanatory.
    """

    #version_ = button_var.get()
    #print(version_)
    global serial_object
    global statePort
    baud = baudlist[baudiosbox.current()]
    port = listPorts[portbox.current()]
    print(port,baud)
    try:
        print('port: '+ str(port), baud)
        serial_object.baudrate = baud
        serial_object.port = port
        serial_object.timeout = 0
        serial_object.open()
        time.sleep(0.1)
        serial_object.flush()
        print('Result: '+str(serial_object.is_open))
    except OSError as err:
        print("Cant Open Specified Port"+str(err))

    if serial_object.is_open:
        statePort = True
        t1 = threading.Thread(target=get_data)
        t1.daemon = True
        t1.start()


def get_data():
    """This function serves the purpose of collecting data from the serial object and storing
    the filtered data into a global variable.
    The function has been put into a thread since the serial event is a blocking function.
    """
    global serial_object
    global filter_data
    global serial_data
    global dataInStr
    global Sp02
    global PRbmp

    while (1):
        try:
            serial_data = serial_object.readline()
            if len(serial_data) > 0:
                dataInStr = ""
                if((serial_data[0] == 1)and(len(serial_data)==9)):
                    Sp02 = str((serial_data[6] & 0x7F))
                    PRbmp = str((serial_data[5] & 0x7F))
                    serial_object.flush()
                else:
                    Sp02 = 'NS'
                    PRbmp = 'NS'
                for c in serial_data:
                   dataInStr = dataInStr + ' ' + str((c & 0x7F))
                print(dataInStr)

            if not statePort:
                serial_object.close()

        except TypeError as err:
            print("Status Port" + str(err))


def update_gui():
    """" This function is an update function which is also threaded. The function assimilates the data
    and applies it to it corresponding progress bar. The text box is also updated every couple of seconds.
    A simple auto refresh function .after() could have been used, this has been avoid purposely due to
    various performance issues.
    """
    global filter_data
    global update_period
    global dataInStr
    global Sp02
    global PRbmp
    new = time.time()

    while (1):
        if dataInStr:
            print("updating data")
            text.insert(tk.END, dataInStr)
            text.insert(tk.END, "\n")
            try:
                # Borrar Valores previos
                Ide_text.delete("1.0", tk.END)
                T0_text.delete("1.0", tk.END)
                # Insertar nuevos valores
                Ide_text.insert("1.0", Sp02)
                T0_text.insert("1.0", PRbmp)

            except:
                pass
            filter_data= ""
            if time.time() - new >= update_period:
                text.delete("1.0", tk.END)
                send1()
                new = time.time()
        time.sleep(2)


def send1():
    hexData =bytearray([0x7D, 0x81, 0xA1, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80])
    print("sending command")
    if serial_object.is_open:
        serial_object.write(hexData)
    else:
        print("Port serial is not open")

#llamado desde el boton
def disconnect():
    """
    This function is for disconnecting and quitting the application.
    Sometimes the application throws a couple of errors while it is being shut down, the fix isn't out yet
    but will be pushed to the repo once done.
    simple GUI.quit() calls.
    """
    print("Good bye")
    global statePort
    try:
        statePort = False
        while serial_object.is_open:
            pass
    except AttributeError:
        print("Closed without Using it -_-")
    gui.quit()

#llamado desde el menu
def disconnect1():
    print("Good bye1")
    global statePort
    try:
        statePort = False
        while serial_object.is_open:
            pass
    except AttributeError:
        print("Closed without Using it -_-")
    gui.quit()


def on_select(event=None):
    print('----------------------------')

    if event: # <-- this works only with bind because `command=` doesn't send event
        print("event.widget:", event.widget.get())

def donothing():
    messagebox.showinfo("Info", "CARLOS RODRIGUEZ carlosdr@unicauca.edu.co ")

#if __name__ == "__main__":
"""
The main loop consists of all the GUI objects and its placement.
The Main loop handles all the widget placements.
"""
# frames
frame_1 = tk.Frame(height=335, width=480, bd=3, relief='groove').place(x=7, y=15)
frame_2 = tk.Frame(height=100, width=480, bd=3, relief='groove').place(x=7, y=360)
text = tk.Text(width=57, height=6)
text.pack()


# threads
t2 = threading.Thread(target=update_gui)
t2.daemon = True
t2.start()

# Labels
data1_ = tk.Label(text="%SpO2: ").place(x=15, y=130)
data2_ = tk.Label(text="PRbpm: ").place(x=15, y=220)
# Labels
Fecha = tk.Label(text="Fecha: ").place(x=245, y=130)
Hora = tk.Label(text="Hora:").place(x=245, y=160)

baud = tk.Label(text="Baud:").place(x=100, y=378)
port = tk.Label(text="Puerto:").place(x=200, y=378)
contact = tk.Label(text="CMS50D+").place(x=250, y=447)

# Variables
Ide_text = tk.Text(width=4, height=1,font=("Helvetica", 32))
Ide_text.tag_configure("center", justify='center')
T0_text = tk.Text(width=4, height=1,font=("Helvetica", 32))
T0_text.tag_configure("center", justify='center')
Fecha_text =   tk.Text(width=15, height=1, bd=-1, relief="flat")
Hora_text =    tk.Text(width=15, height=1, bd=-1, relief="flat")
Ide_text.insert("1.0", "00")

# ubicacion
text.place(x=15, y=20)
Ide_text.place(x=80, y=130)
T0_text.place(x=80, y=220)

Fecha_text.place(x=300, y=130)
Hora_text.place(x=300, y=160)

# Entry

baudiosbox = ttk.Combobox(gui,width=7)
baudiosbox["values"] = baudlist
baudiosbox.bind("<<ComboboxSelected>>", lambda _: print(baudiosbox.current()))
baudiosbox.current(5)
baudiosbox.pack()
baudiosbox.place(x=100, y=395)
listPorts = SerialFCnCms.serial_ports()
portbox = ttk.Combobox(gui, width=9)
portbox["values"] = listPorts
portbox.bind("<<ComboboxSelected>>", lambda _: print(portbox.current()))
if len(listPorts) >0:
    portbox.current(0)
portbox.pack()
portbox.place(x=200, y=395)


# button
button2 = tk.Button(text="Leer", command=send1, width=6).place(x=15, y=310)
connect = tk.Button(text="Conectar", command=connect).place(x=15, y=390)
disconnect = tk.Button(text="Desconectar", command=disconnect).place(x=300, y=390)

#Menu
menubar = tk.Menu(gui)
filemenu = tk.Menu(menubar, tearoff = 0)
filemenu.add_command(label="Nuevo", command = donothing)
filemenu.add_command(label = "Abrir", command = donothing)
filemenu.add_separator()
filemenu.add_command(label = "Salir", command = disconnect1)
menubar.add_cascade(label = "Archivo", menu = filemenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label = "Ayuda", command = donothing)
helpmenu.add_command(label = "Acerca de...", command = donothing)
menubar.add_cascade(label = "Ayuda", menu = helpmenu)

# display the menu
gui.config(menu=menubar)

# mainloop
gui.geometry('500x500')
gui.mainloop()

