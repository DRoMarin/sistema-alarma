import tkinter as tk
from queue import Queue

panel_buffer = Queue(maxsize = 8)
panel_screen_buffer = []

button_labels = ["1","2","3","Esc"  ,
                 "4","5","6","Enter",
                 "7","8","9","PANIC",
                 "*","0","#","INCEN"]

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
        case "Esc" :
            panel_buffer.queue.clear()
        case "Enter":
            print(*list(panel_buffer.queue),sep=" ")
            panel_buffer.queue.clear()
        case _:
            print("TBD")


##### configuracion ventana principal
panel = tk.Tk()
#panel.title('PANEL SIMULADOR')label
#tamaño
panel_w = 1000
panel_h = 200
#centrado
screen_w = panel.winfo_screenwidth()
screen_h = panel.winfo_screenheight()
center_y = int(screen_h/2)# - panel_h/2) 
center_x = int(screen_w/2)# - panel_w/2)

#panel.geometry(f'{panel_w}x{panel_h}+{center_x}+{center_y}')
panel.resizable(False,False)



#array de botones
pixel = tk.PhotoImage(width = 1,height = 1)
B_arr = [0,0]*len(button_labels)
for label_idx in range(len(button_labels)):
    B_arr[label_idx] = tk.Button(panel,
                                 text=button_labels[label_idx],
                                 width = 200, height = 50,
                                 padx=0,pady=0,
                                 image=pixel, 
                                 compound='center',
                                 highlightthickness=0,
                                 command=lambda i = label_idx: buttonCallback(i))
    B_arr[label_idx].grid(row = (label_idx//4), column = (label_idx % 4))

panel.grid_columnconfigure(1,weight=0)

#B = tk.Button(panel, text = "APRETAR", command = buttonCallback)
#B.pack()
panel.mainloop()

