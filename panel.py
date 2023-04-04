import tkinter as tk
from queue import Queue

panel = tk.Tk()
panel_screen_buffer = tk.StringVar()
#panel_screen_buffer.set("--------")
panel_buffer = Queue(maxsize = 8)
sensor_num = 16

button_labels = ["1","2","3","Esc"  ,
                 "4","5","6","Enter",
                 "7","8","9","PANIC",
                 "*","0","#","INCEN"]

def updateScreen(input_buffer):
    buffer = list(input_buffer.queue)
    panel_screen_buffer.set(''.join(buffer))

def buttonCallback(button_pressed):
    label = button_labels[button_pressed]
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
            print(*list(panel_buffer.queue),sep="")
            panel_buffer.queue.clear()
            updateScreen(panel_buffer)
        case _:
            print("TBD")

##### configuracion ventana principal
panel.title('PANEL SIMULADOR')
#tamaño
panel_w = 1100
panel_h = 250
#centrado
screen_w = panel.winfo_screenwidth()
screen_h = panel.winfo_screenheight()
center_y = int(screen_h/2)# - panel_h/2) 
center_x = int(screen_w/2)# - panel_w/2)

#panel.geometry(f'{panel_w}x{panel_h}+{center_x}+{center_y}')
panel.resizable(False,False)

#panel screen
panel_screen_frame = tk.LabelFrame(panel, height=110,borderwidth=3,highlightthickness=5)
panel_screen_frame.grid(row=0,column=0,columnspan=4,sticky='nsew')
panel_screen_frame.pack_propagate(0)
panel_screen = tk.Label(panel_screen_frame,
                        textvariable=panel_screen_buffer,
                        font=('Consolas',40))
panel_screen.pack(side="top")

#array de botones
pixel = tk.PhotoImage(width = 1,height = 1)
B_arr = [0,0]*len(button_labels)
for label_idx in range(len(button_labels)):
    B_arr[label_idx] = tk.Button(panel,
                                 text=button_labels[label_idx],
                                 width = 50, height = 50,
                                 padx=0,pady=0,
                                 image=pixel, 
                                 compound='center',
                                 highlightthickness=5,
                                 borderwidth=3,
                                 command=lambda i = label_idx: buttonCallback(i))
    B_arr[label_idx].grid(row = (label_idx//4)+1, column = (label_idx % 4),sticky="ew")

spacing = tk.Label(panel,text="",font=('Consolas',40),width=2)
spacing.grid(row=1, column=4)

# Array de sensores
S_arr = [0,0]*sensor_num
for sensor_idx in range(sensor_num):
    S_arr[sensor_idx] = tk.Button(panel,
                                 text=str(sensor_idx),
                                 width = 50, height = 50,
                                 padx=0,pady=0,
                                 image=pixel, 
                                 compound='center',
                                 highlightthickness=5,
                                 borderwidth=3,
                                 #command=lambda i = label_idx: buttonCallback(i)
                                 )
    S_arr[sensor_idx].grid(column = (sensor_idx//4)+5, row = (sensor_idx % 4)+1)



panel.mainloop()

