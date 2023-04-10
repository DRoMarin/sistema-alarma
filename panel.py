import tkinter as tk
from queue import Queue
import time
import threading as th


#########################################################################
###################           PANEL FRONTAL           ###################
#########################################################################
panel = tk.Tk()
panel_screen_buffer = tk.StringVar()
panel_buffer = Queue(maxsize = 8)
sensor_num = 16
#panel_screen_buffer.set("--------")

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

#########################################################################
#####################       MAQUINA DE ESTADOS      #####################
#########################################################################

#diccionario valores monitor
estados = {
    "Armado":1,
    "Alarma":3,
    "Inactivo":0
}
subestados = {
    "Zona":1,
    "Armado":3,
    "Usuario":5,
    "Telefono":7,
    "Bloqueo":15,
    "Espera":0
}
modo = {
    "NA" : 0,
    "Zona 0": 5,
    "Zona 1": 10 
}
alarma = {
    "NA" : 0,
    "Incendio": 12,
    "Panico": 2,
    "Allanamiento": 15  
}
bocina = {
    "Apagado" : 0,
    "Intermitente" : 1,
    "Permanente" : 3,
}
fuente = {
    "AC" : 0,
    "Bateria" : 1
}
llamada = {
    "Presente" : 1,
    "Espera" : 3,
    "No Presente" : 0
}

class State(object):
    def __init__(self):
        pass
    @property
    def name(self):
        return ''
    def enter(self, machine):
        pass
    def exit(self, machine):
        pass
    def update(self, machine):
        pass

class StateMachine(object):
    def __init__(self):
        self.state = None
        self.states = {} #dictionary
        #self.buffer_update = False
        
        self.EstadoActual = None
        self.SubestadoActual = None
        self.EstadoReportado = None
        self.ModoArmado = 0
        self.TipoAlarma = 0
        self.AccionBocina = 0
        self.FuenteActiva = 0
        self.SolicitudLlamada = 0
        self.ClavesInvalidas = 0

    def add_state(self,state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            print('SALIENDO %s' %(self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        print('ENTRANDO %s' %(self.state.name))
        self.state.enter(self)

    def update(self):
        if self.state:
            #TENTATIVO TBD: CHECK BOTONES DE PANICO/INCENDIO
            #print('ACTUALIZANDO %s' %(self.state.name))
            self.state.update(self)

    def reset(self):
        pass
## INICIO SUPERESTADO INACTIVO
class estadoEspera(State):
    @property
    def name(self):
        return "Espera"
    def enter(self, machine):
        State.enter(self, machine)
    def exit(self, machine):
        State.exit(self, machine)
    def update(self, machine):
        #print("ESPERANDO...")
        if panel_event.is_set():
            command = panel_queue.get()
            print(command)
            panel_event.clear()
            machine.go_to_state("Bloqueo")

class subestadoArmado(State):
    @property
    def name(self):
        return "Armado"
    def enter(self, machine):
        State.enter(self, machine)
    def exit(self, machine):
        State.exit(self, machine)
    def update(self, machine):
        #TBD
        pass
        

class subestadoZona(State):
    @property
    def name(self):
        return "Zona"
    def enter(self, machine):
        State.enter(self, machine)
    def exit(self, machine):
        State.exit(self, machine)
    def update(self, machine):
        #TBD
        pass
        

class subestadoUsuario(State):
    @property
    def name(self):
        return "Usuario"
    def enter(self, machine):
        State.enter(self, machine)
    def exit(self, machine):
        State.exit(self, machine)
    def update(self, machine):
        #TBD
        pass
        

class subestadoTelefono(State):
    @property
    def name(self):
        return "Telefono"
    def enter(self, machine):
        State.enter(self, machine)
    def exit(self, machine):
        State.exit(self, machine)
    def update(self, machine):
        #TBD
        pass
        

class subestadoBloqueo(State):
    @property
    def name(self):
        return "Bloqueo"
    #def enter(self, machine):
    #    State.enter(self, machine)
    def exit(self, machine):
        panel_buffer.queue.clear()
        panel_queue.queue.clear()
        panel_event.clear()
    def update(self, machine):
        time.sleep(5) #TBD: CAMBIAR A 5 MIN
        machine.go_to_state("Espera")
## FIN SUPERESTADO INACTIVO

####    THREAD LOOP    ####
def systemTask():

    machine = StateMachine()
    machine.add_state(estadoEspera())
    machine.add_state(subestadoBloqueo())
    machine.go_to_state('Espera')
    while True:
        if close_event.is_set():
            break
        machine.update()
    print("CERRANDO")

#eventos
panel_event = th.Event()
close_event = th.Event()

#colas
panel_queue = Queue()

#main
system_thread = th.Thread(target=systemTask)
system_thread.start()
panel.mainloop()
close_event.set()
system_thread.join()