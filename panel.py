import tkinter as tk
from queue import Queue
import playsound as ps
import time
import threading as th


#########################################################################
###################           PANEL FRONTAL           ###################
#########################################################################
panel = tk.Tk()
screen_string = tk.StringVar()
slide_value = tk.DoubleVar()
panel_buffer = Queue(maxsize = 9) #buffer interno del indicador del panel
sensor_num = 16
sensor_buffer = ["0xfff3c000"]*16
#screen_string.set("--------")

button_labels = ["1","2","3","Esc"  ,
                 "4","5","6","Enter",
                 "7","8","9","PANIC",
                 "*","0","#","INCEN"]

led_labels = ["MODO 0","MODO 1","BATT"]

def updateScreen(input_queue):
    buffer = list(input_queue.queue)
    screen_string.set(''.join(buffer))

def buttonCallback(button_pressed):
    label = button_labels[button_pressed]
    match label:
        case index if label in ["1","2","3","4","5","6","7","8","9","*","0","#"]:
            #print(label)
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
            #print("EN BUFFER: " + command)
            panel_queue.put(command)
            keyboard_event.set()
            panel_buffer.queue.clear()
            updateScreen(panel_buffer)
        case "PANIC":
            panic_event.set()
            keyboard_event.set()
        case "INCEN":
            incen_event.set()
            keyboard_event.set()
           
def sensorCallback(sensor_pressed):
    sensor_buffer[sensor_pressed] = "0x55596aaa"
    #print(sensor_pressed)
    sensor_event.set()
def llamadaCallback():
    llamada_event.set()
    
##### configuracion ventana principal
panel.title('PANEL SIMULADOR')
#tamaño
panel.resizable(False,False)

#panel screen
panel_screen_frame = tk.LabelFrame(panel, height = 130,borderwidth = 3,highlightthickness = 5)
panel_screen_frame.grid(row = 0,column = 0,columnspan = 4,sticky = 'nsew')
panel_screen_frame.pack_propagate(0)
panel_screen = tk.Label(panel_screen_frame,
                        textvariable = screen_string,
                        font = ('Consolas',40))
panel_screen.pack(side = "top")

led_screen_frame = tk.LabelFrame(panel_screen_frame,
                                 height = 30,
                                 width = 1000,
                                 borderwidth = 1,
                                 highlightthickness = 0)
led_screen_frame.pack(side="bottom")

#Indicadores LED
led_arr = []
for ind_idx in range(len(led_labels)):
    pair = [0,0]
    pair[0]= tk.Label(led_screen_frame,
                      text= led_labels[ind_idx],
                      font = ('Consolas',10))
    

    pair[1]= tk.Canvas(led_screen_frame,
                       width = 20,
                       height = 20,
                       bg = 'gray')
    
    pair[0].grid(row = 0, column = ind_idx*2)
    pair[1].grid(row = 0, column = ind_idx*2+1)
    led_arr.append(pair)


#array de botones
pixel = tk.PhotoImage(width = 1,height = 1)
B_arr = []
for label_idx in range(len(button_labels)):
    button = tk.Button(panel,
                       text = button_labels[label_idx],
                       width = 50, height = 50,
                       padx = 0,pady = 0,
                       image = pixel, 
                       compound = 'center',
                       highlightthickness = 5,
                       borderwidth = 3,
                       command = lambda i = label_idx: buttonCallback(i))
    button.grid(row = (label_idx//4)+1, column = (label_idx % 4),sticky="ew")
    B_arr.append(button)

spacing = tk.Label(panel,text="",font=('Consolas',40),width=2)
spacing.grid(row=1, column=4)

# Array de sensores
S_arr = []
for sensor_idx in range(sensor_num):
    sensor = tk.Button(panel,
                       text = str(sensor_idx),
                       width = 50, height = 50,
                       padx = 0,pady = 0,
                       image = pixel, 
                       compound ='center',
                       highlightthickness = 5,
                       borderwidth = 3,
                       command = lambda i = sensor_idx: sensorCallback(i))
    sensor.grid(column = (sensor_idx//4)+5, row = (sensor_idx % 4)+1)
    S_arr.append(sensor)

boton_llamada = tk.Button(panel,
                       text = "CONTESTAR",
                       width = 100, height = 50,
                       padx = 0,pady = 0,
                       image = pixel, 
                       compound ='center',
                       highlightthickness = 5,
                       borderwidth = 3,
                       command = llamadaCallback)

boton_llamada.grid(column = 7, row = 0,columnspan=2)


dial_voltaje = tk.Scale(panel, from_=0, to= 220,orient="horizontal",variable=slide_value)
dial_voltaje.grid(column = 5, row = 0, columnspan=2)
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
    "CodArmado":3,
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
        self.ContraInvalidas = 0

        self.ContraUsuario = ""
        self.ContraSistema = ""
        self.ClaveArmado = ""
        self.NumeroUsuario = ""
        self.TelefonoAgencia = ""
        self.ConteoBatNeg = 0
        self.ConteoBatPos = 0

    def add_state(self,state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            print('SALIENDO %s' %(self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        print('ENTRANDO %s' %(self.state.name))

        #panic_event.clear()
        #incen_event.clear()
        keyboard_event.clear()

        panel_buffer.queue.clear()
        panel_queue.queue.clear()
        
        self.state.enter(self)

    def update(self):
        if self.state:
            if (panic_event.is_set() or incen_event.is_set()):
                self.EstadoReportado = estados["Alarma"]

                if panic_event.is_set():
                    self.TipoAlarma = alarma["Panico"]
                elif incen_event.is_set():
                    self.TipoAlarma = alarma["Incendio"]

                self.SolicitudLlamada = llamada["Presente"]
                self.AccionBocina = bocina["Intermitente"]

                self.go_to_state("Alarma") 
            #print(slide_value.get())
            if slide_value.get() < 110.0 and self.ConteoBatNeg < 5:
                self.ConteoBatNeg += 1
                if self.ConteoBatNeg == 5:
                    led_arr[2][1].configure(bg='red')
                    self.ConteoBatPos = 0
            elif slide_value.get() > 110.0 and self.ConteoBatPos < 30:
                self.ConteoBatPos += 1
                if self.ConteoBatPos == 30:
                    led_arr[2][1].configure(bg='gray')
                    self.ConteoBatNeg = 0
            self.state.update(self)
            time.sleep(0.1)

    def reset(self):
        pass

## INICIO SUPERESTADO INACTIVO
class estadoEspera(State):
    @property
    def name(self):
        return "Espera"
    #def enter(self, machine):
    #    State.enter(self, machine)
    #def exit(self, machine):
    #    State.exit(self, machine)
    def update(self, machine):
        
        state_change = "Espera"
        if not panel_queue.empty():
            keyboard_event.wait()
            keyboard_event.clear()
            command = panel_queue.get()[-4:]
            if command == machine.ContraUsuario:
                machine.ContraInvalidas = 0
                print("CONTRASEÑA USUARIO VALIDA")
                state_change = validacionComando("Usuario",machine)
            elif command == machine.ContraSistema:
                machine.ContraInvalidas = 0
                print("CONTRASEÑA SISTEMA VALIDA")
                state_change = validacionComando("Sistema",machine)
            elif machine.ContraInvalidas < 2:
                machine.ContraInvalidas += 1
            else:
                machine.ContraInvalidas = 0
                state_change = "Bloqueo"

            if state_change in subestados:
                machine.SubestadoActual = subestados[state_change]
            else:
                machine.EstadoReportado = estados[state_change]

        #print(state_change)
        if state_change != "Espera":
            machine.go_to_state(state_change)
         
class subestadoCodArmado(State):
    @property
    def name(self):
        return "CodArmado"
    def update(self, machine):
        keyboard_event.wait()
        value = panel_queue.get()
        if len(value) == 4 and not valorInvalido(value):
            with open("pswd.txt",'r+') as pswd_file:
                machine.ClaveArmado = value
                pswd_file.writelines(machine.ContraSistema
                                     +machine.ContraUsuario
                                     +machine.ClaveArmado)
        machine.go_to_state("Espera")
        machine.SubestadoActual = subestados["Espera"]
        
class subestadoZona(State):
    @property
    def name(self):
        return "Zona"
    def update(self, machine):
        newlines = []
        with open("sensorcfg.txt",'r') as sensorcfg:
            for line in sensorcfg:
                num = line[:2]
                zona = line[2]
                mode = line[3]
                panel_buffer.put(num)
                panel_buffer.put("-")
                panel_buffer.put(zona)
                updateScreen(panel_buffer)
                panel_buffer.queue.clear()
                keyboard_event.wait()
                value = panel_queue.get()
                if value in ["0","1"]:
                    zona = value    
                newlines.append(num+zona+mode+"\n")
                keyboard_event.clear()      
        with open("sensorcfg.txt",'w+') as sensorcfg:
            sensorcfg.writelines(newlines)
        machine.go_to_state("Espera") 
        machine.SubestadoActual = subestados["Espera"]

class subestadoUsuario(State):
    @property
    def name(self):
        return "Usuario"
    def update(self, machine):
        keyboard_event.wait()
        value = panel_queue.get() ##########
        if not valorInvalido(value) and len(value) == 9:
            machine.NumeroUsuario = value
            actualizarSysCfg(machine)
        machine.go_to_state("Espera") 
        machine.SubestadoActual = subestados["Espera"]
        
class subestadoTelefono(State):
    @property
    def name(self):
        return "Telefono"
    def update(self, machine):
        keyboard_event.wait()
        value = panel_queue.get() 
        if not valorInvalido(value)and len(value) == 8:
            machine.TelefonoAgencia = value
            actualizarSysCfg(machine)    
        machine.go_to_state("Espera") 
        machine.SubestadoActual = subestados["Espera"]

class subestadoBloqueo(State):
    @property
    def name(self):
        return "Bloqueo"
    def update(self, machine):
        time.sleep(5) #TBD: CAMBIAR A 5 MIN
        machine.go_to_state("Espera")
        machine.SubestadoActual = subestados["Espera"]
## FIN SUPERESTADO INACTIVO


class estadoArmado(State):
    @property
    def name(self):
        return "Armado"
    def enter(self, machine):
        zona = None
        if machine.ModoArmado == modo["Zona 0"]:
            zona = 0
        elif machine.ModoArmado == modo["Zona 1"]:
            zona = 1
        led_arr[zona][1].configure(bg='red')
        panel_buffer.put("ARMD")
        updateScreen(panel_buffer)
        time.sleep(5)
        panel_buffer.queue.clear()
        updateScreen(panel_buffer)
        State.enter(self, machine)

    def update(self, machine):
        time.sleep(0.5)
        with sensor_lock:
            zona = None
            if machine.ModoArmado == modo["Zona 0"]:
                zona = 0
            elif machine.ModoArmado == modo["Zona 1"]:
                zona = 1
            with open("sensorcfg.txt",'r') as sensorcfg:
                for line in sensorcfg.readlines():
                    #time.sleep(0.5)      
                    if line[3] == "1" and (line[2] == str(zona) or zona == "0"):
                        machine.EstadoReportado = estados["Alarma"]
                        machine.TipoAlarma = alarma["Allanamiento"]
                        if zona == 1:
                            machine.AccionBocina = bocina["Intermitente"]
                        elif zona == 0:
                            machine.AccionBocina = bocina["Permanente"]
                            machine.SolicitudLlamada = llamada["Presente"]
                        machine.go_to_state("Alarma")
        if keyboard_event.is_set() and not panel_queue.empty():
            keyboard_event.clear()
            command = panel_queue.get()[-4:]
            if command == machine.ClaveArmado:
                machine.EstadoReportado = estados["Inactivo"]
                machine.SubestadoActual = subestados["Espera"]
                machine.go_to_state("Espera")

class estadoAlarma(State):
    @property
    def name(self):
        return "Alarma"
    def enter(self,machine):
        panic_event.clear()
        incen_event.clear()
        if machine.AccionBocina == bocina["Intermitente"]:
            PWM_queue.put(50)
            if machine.TipoAlarma == alarma["Allanamiento"] and machine.ModoArmado == modo["Zona 1"]:
                alarmaTimer = th.Timer(5, alarmaTimerTask)
                alarmaTimer.start()
        elif machine.AccionBocina == bocina["Permanente"]:
            PWM_queue.put(100)
    def update(self, machine):

        if alarma_event.is_set():
            alarma_event.clear()
            PWM_queue.put(100)
            machine.AccionBocina = bocina["Permanente"]

        if machine.SolicitudLlamada == llamada["Presente"]:
            machine.SolicitudLlamada = llamada["Espera"]
            print("Marcando... " + machine.TelefonoAgencia)
        elif machine.SolicitudLlamada == llamada["Espera"] and llamada_event.is_set():
            #machine.SolicitudLlamada = llamada["No Presente"]
            if machine.TipoAlarma == alarma["Panico"]:
                print("PANICO", machine.NumeroUsuario) #TTS
                
            elif machine.TipoAlarma == alarma["Incendio"]:
                print("INCENDIO", machine.NumeroUsuario)

            elif machine.TipoAlarma == alarma["Allanamiento"]:
                print(machine.NumeroUsuario)
            time.sleep(1)

        if keyboard_event.is_set() and not panel_queue.empty():
            keyboard_event.clear()
            command = panel_queue.get()[-4:]
            if command == machine.ClaveArmado:
                PWM_queue.put(0)
                machine.go_to_state("Espera")
                machine.EstadoReportado = estados["Inactivo"]
                machine.TipoAlarma = alarma["NA"]
                machine.AccionBocina = bocina["Apagado"]
                machine.SolicitudLlamada = llamada["No Presente"]
                machine.SubestadoActual = subestados["Espera"]


def validacionComando(tipo,machine):
    command = ""
    while True:
        flag = keyboard_event.wait(timeout=10)
        keyboard_event.clear()
        if flag == False:
            print("TIEMPO")
            return "Espera"
        elif flag == True and not panel_queue.empty():
            command = panel_queue.get()[-4:] 
        #print("COMANDO: " + command)
        if tipo == "Usuario":
            match command:
                case "#99#":
                    return "Zona"
                case "#66#":
                    return "CodArmado"
                case "*0*0":
                    print("ARMADO MODO 0")
                    machine.ModoArmado = modo["Zona 0"]
                    return "Armado"
                case "*1*1":
                    print("ARMADO MODO 1")
                    machine.ModoArmado = modo["Zona 1"]
                    return "Armado"
                case _:
                    return "Espera" 
        elif tipo == "Sistema":
            match command:
                case "#33#":
                    return "Usuario"
                case "#**#":
                    return "Telefono"
                case _:
                    return "Espera" 
        else:
            return "Espera"

def valorInvalido(value):
    return any(item in value for item in ["#","*"])
  
def actualizarSysCfg(machine):
    with open("syscfg.txt",'r+') as syscfg_file:
        print(machine.NumeroUsuario
              +machine.TelefonoAgencia)
        syscfg_file.writelines(machine.NumeroUsuario
                               +machine.TelefonoAgencia)   
def alarmaTimerTask():
    alarma_event.set()

####    THREAD LOOP    ####
def systemTask():
    #cargar contras
    pswd = ""
    syscfg = ""
    sensorcfg = ""
    with open("pswd.txt",'r+') as pswd_file:
        pswd = pswd_file.read()
    with open("syscfg.txt",'r+') as syscfg_file:
        syscfg = syscfg_file.read()
    with open("sensorcfg.txt",'r') as sensorcfg_file: 
        sensorcfg = sensorcfg_file.readlines()
    with open("sensorcfg.txt",'w+') as sensorcfg_file: 
        for idx in range(16):
            sensorcfg_file.write(str(idx).zfill(2)+sensorcfg[idx][2]+"0\n") 

    machine = StateMachine()
    machine.add_state(estadoEspera())
    machine.add_state(subestadoBloqueo())
    machine.add_state(subestadoZona())
    machine.add_state(subestadoCodArmado())
    machine.add_state(subestadoUsuario())
    machine.add_state(subestadoTelefono())
    machine.add_state(estadoArmado())
    machine.add_state(estadoAlarma())
    machine.go_to_state('Espera')

    #machine.contraSistema = pswd_file.read()
    machine.ContraSistema = pswd[0:4]
    machine.ContraUsuario = pswd[4:8]
    machine.ClaveArmado = pswd[8:12]

    machine.NumeroUsuario = syscfg[:9]
    machine.TelefonoAgencia = syscfg[9:17]

    print(machine.ContraUsuario)
    print(machine.TelefonoAgencia)

    while True:
        if close_event.is_set():
            break
        machine.update()
    print("CERRANDO")


def sensorTask():
    while True:
        if close_event.is_set():
            break
        sensor_event.wait()
        sensor_event.clear()
        with sensor_lock:
            lines = []
            with open("sensorcfg.txt",'r+') as sensorcfg: 
                lines = sensorcfg.readlines()
                for idx in range(16):
                    if sensor_buffer[idx] == "0x55596aaa":
                        zona = lines[idx][2]
                        lines[idx] = str(idx).zfill(2)+zona+"1\n"     
            with open("sensorcfg.txt",'w+') as sensorcfg:     
                sensorcfg.writelines(lines)

def reproducirAlarma():
        PWM = 0
        while(True):
            if not PWM_queue.empty():      
                PWM = PWM_queue.get()
            if PWM == 50:
                ps.playsound('beep.mp3')
                time.sleep(1)
            elif PWM == 100:
                ps.playsound('beep.mp3', block=False)
                time.sleep(0.5)
            if close_event.is_set():
                break
                

#eventos
close_event = th.Event() #cierre de la interfaz
keyboard_event = th.Event() #introducir comando o teclas
panic_event = th.Event() #boton panico
incen_event = th.Event() #boton incendio
sensor_event = th.Event()
alarma_event = th.Event()
llamada_event = th.Event()

#colas
PWM = 0
PWM_queue = Queue()
panel_queue = Queue()#cola de datos para sistema
#mutex
sensor_lock = th.Lock()
#main
system_thread = th.Thread(target=systemTask)
sensor_thread = th.Thread(target=sensorTask)
alarma_thread = th.Thread(target=reproducirAlarma)

sensor_thread.start()
system_thread.start()
alarma_thread.start()

panel.mainloop()
close_event.set()
keyboard_event.set()
sensor_event.set()
sensor_thread.join()
alarma_thread.join()
system_thread.join()