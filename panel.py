import tkinter as tk
from queue import Queue
import time
import threading as th

#import sistema

panel = tk.Tk()
panel_screen_buffer = tk.StringVar()
#panel_screen_buffer.set("--------")
panel_buffer = Queue(maxsize = 8)
sensor_num = 16


button_labels = ["1","2","3","Esc"  ,
                 "4","5","6","Enter",
                 "7","8","9","PANIC",
                 "*","0","#","INCEN"]

led_labels = ["MODO 0","MODO 1","BATT"]

def updateScreen(input_buffer):
    buffer = list(input_buffer.queue)
    panel_screen_buffer.set(''.join(buffer))

def buttonCallback(button_pressed):
    label = button_labels[button_pressed]
    #TBD: AGREGAR FUNCIONES SISTEMA
    match label:
        case index if label in ["1","2","3","4","5","6","7","8","9","*","0","#"]:
            print(label)
            if panel_buffer.full():
                panel_buffer.get()
                panel_buffer.put(label)
            else:
                panel_buffer.put(label)
            updateScreen(panel_buffer)
        case "Esc" :
            panel_buffer.queue.clear()
            updateScreen(panel_buffer)
        case "Enter":
            command = ''.join(panel_buffer.queue)
            print(command)
            panel_queue.put(command)
            panel_event.set()
            panel_buffer.queue.clear()
            updateScreen(panel_buffer)
        case _:
            print("TBD") #################################################

def sensorCallback(sensor_pressed):
    #TBD: AGREGAR FUNCIONES SISTEMA
    print(sensor_pressed)

def systemTask():
    while True:
        if close_event.is_set():
            break
        if panel_event.is_set():
            command = panel_queue.get()
            print(command)
            panel_event.clear()
    print("CERRANDO")
    

##### configuracion ventana principal
panel.title('PANEL SIMULADOR')
#tamaño
panel.resizable(False,False)

#panel screen
panel_screen_frame = tk.LabelFrame(panel, height = 130,borderwidth = 3,highlightthickness = 5)
panel_screen_frame.grid(row = 0,column = 0,columnspan = 4,sticky = 'nsew')
panel_screen_frame.pack_propagate(0)
panel_screen = tk.Label(panel_screen_frame,
                        textvariable = panel_screen_buffer,
                        font = ('Consolas',40))
panel_screen.pack(side = "top")

led_screen_frame = tk.LabelFrame(panel_screen_frame,
                                 height = 30,
                                 width = 1000,
                                 borderwidth = 1,
                                 highlightthickness = 0)
led_screen_frame.pack(side="bottom")

#Indicadores LED
led_arr = [[0]*2]*len(led_labels)
for ind_idx in range(len(led_labels)):
    led_arr[ind_idx][0] = tk.Label(led_screen_frame,
                                   text= led_labels[ind_idx],
                                   font = ('Consolas',10))
    
    led_arr[ind_idx][1] = tk.Canvas(led_screen_frame,
                                    width = 20,
                                    height = 20,
                                    bg = 'gray')
    
    led_arr[ind_idx][0].grid(row = 0, column = ind_idx*2)
    led_arr[ind_idx][1].grid(row = 0, column = ind_idx*2+1)


#array de botones
pixel = tk.PhotoImage(width = 1,height = 1)
B_arr = [0]*len(button_labels)
for label_idx in range(len(button_labels)):
    B_arr[label_idx] = tk.Button(panel,
                                 text = button_labels[label_idx],
                                 width = 50, height = 50,
                                 padx = 0,pady = 0,
                                 image = pixel, 
                                 compound = 'center',
                                 highlightthickness = 5,
                                 borderwidth = 3,
                                 command = lambda i = label_idx: buttonCallback(i))
    B_arr[label_idx].grid(row = (label_idx//4)+1, column = (label_idx % 4),sticky="ew")

spacing = tk.Label(panel,text="",font=('Consolas',40),width=2)
spacing.grid(row=1, column=4)

# Array de sensores
S_arr = [0]*sensor_num
for sensor_idx in range(sensor_num):
    S_arr[sensor_idx] = tk.Button(panel,
                                 text = str(sensor_idx),
                                 width = 50, height = 50,
                                 padx = 0,pady = 0,
                                 image = pixel, 
                                 compound ='center',
                                 highlightthickness = 5,
                                 borderwidth = 3,
                                 command = lambda i = sensor_idx: sensorCallback(i))
    S_arr[sensor_idx].grid(column = (sensor_idx//4)+5, row = (sensor_idx % 4)+1)

system_thread = th.Thread(target=systemTask)

#eventos
panel_event = th.Event()
close_event = th.Event()
#colas
panel_queue = Queue()

system_thread.start()
panel.mainloop()
close_event.set()
system_thread.join()