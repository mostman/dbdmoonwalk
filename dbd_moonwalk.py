import tkinter as tk
from tkinter import ttk
import json
import os
import threading
import time
import random
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from PIL import Image, ImageTk

class DBDMoonwalk:
    def __init__(self):
        # Interface
        self.root = tk.Tk()
        self.root.title("DBD Moonwalk By Eve")
        self.root.geometry("700x650")  # Slightly taller to accommodate GIF
        self.root.configure(bg="#000000")  # Pure black background
        self.root.resizable(False, False)
        
        # Cores
        self.bg_color = "#000000"  # Black background
        self.text_color = "#dddddd"
        self.accent_color = "#aa0000"
        self.active_color = "#00aa00"
        self.key_inactive_color = "#333333"
        self.key_active_color = "#00aa00"
        
        # Controladores
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        # Estado
        self.running = False
        self.moonwalk_active = False
        self.recording = False
        self.record_target = None
        
        # Estado das teclas
        self.key_states = {
            'w': False,
            'a': False,
            'd': False,
            's': False,
            'shift': False
        }
        
        # Thread e listeners
        self.key_thread = None
        self.key_listener = None
        self.mouse_listener = None
        self.emergency_listener = None
        
        # Contador para A/D
        self.ad_counter = 0
        self.ad_last_time = 0
        self.ad_interval = 0.15  # Intervalo mais curto para maior precisão
        self.ad_transition_time = 0.02  # Tempo de transição menor para maior precisão
        
        # Movimento do mouse
        self.mouse_move_amount = 15  # Quantidade que o mouse se move em pixels
        self.mouse_move_timer = 0
        self.last_mouse_move_time = 0
        self.mouse_move_delay = 0.02  # Delay para movimentação do mouse
        
        # Configurações padrão
        self.config = {
            "activation_key": "x1",
            "emergency_key": "f12",
            "w_active": True,
            "s_active": False,
            "shift_active": True,
            "a_active": False,
            "d_active": False,
            "hold_to_activate": False,
            "mouse_macro_enabled": False,
            "mouse_macro_button": "left",
            "mouse_movement_enabled": False,
            "mouse_movement_inverse": False
        }
        
        # Carregar configurações se existirem
        self.load_config()
        
        # Criar interface
        self.create_ui()
        
        # Definir handler para fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Iniciar listener de emergência permanente
        self.start_emergency_listener()

    def create_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título na parte superior
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = tk.Label(title_frame, text="DBD MOONWALK", font=("Arial", 16, "bold"), 
                       bg=self.bg_color, fg=self.accent_color)
        title.pack(side=tk.LEFT)
        
        # Status
        status_frame = tk.Frame(title_frame, bg=self.bg_color)
        status_frame.pack(side=tk.RIGHT)
        
        status_label = tk.Label(status_frame, text="Status:", bg=self.bg_color, fg=self.text_color)
        status_label.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(status_frame, text="DESATIVADO", bg=self.bg_color, fg="red", font=("Arial", 10, "bold"))
        self.status_text.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separador
        separator = tk.Frame(main_frame, height=1, bg=self.accent_color)
        separator.pack(fill=tk.X, pady=10)
        
        # Container principal dividido horizontalmente
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lado esquerdo - Teclas e Controles
        left_frame = tk.Frame(content_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame de teclas
        keys_frame = tk.LabelFrame(left_frame, text="TECLAS AUTOMÁTICAS", bg=self.bg_color, fg=self.text_color, padx=10, pady=10)
        keys_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid de checkboxes para teclas - 2 colunas para tornar mais compacto
        self.w_var = tk.BooleanVar(value=self.config["w_active"])
        self.s_var = tk.BooleanVar(value=self.config["s_active"])
        self.shift_var = tk.BooleanVar(value=self.config["shift_active"])
        self.a_var = tk.BooleanVar(value=self.config["a_active"])
        self.d_var = tk.BooleanVar(value=self.config["d_active"])
        self.hold_var = tk.BooleanVar(value=self.config["hold_to_activate"])
        self.mouse_macro_var = tk.BooleanVar(value=self.config["mouse_macro_enabled"])
        self.mouse_movement_var = tk.BooleanVar(value=self.config["mouse_movement_enabled"])
        self.mouse_movement_inverse_var = tk.BooleanVar(value=self.config["mouse_movement_inverse"])
        
        # Criar grid de checkboxes
        keys_grid = tk.Frame(keys_frame, bg=self.bg_color)
        keys_grid.pack(fill=tk.X)
        
        # Coluna 1
        col1 = tk.Frame(keys_grid, bg=self.bg_color)
        col1.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        # Coluna 2
        col2 = tk.Frame(keys_grid, bg=self.bg_color)
        col2.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        # W na coluna 1
        w_check = tk.Checkbutton(col1, text="W", variable=self.w_var, bg=self.bg_color, 
                               fg=self.text_color, selectcolor=self.bg_color, 
                               activebackground=self.bg_color, activeforeground=self.text_color)
        w_check.pack(anchor=tk.W)
        
        # S na coluna 1
        s_check = tk.Checkbutton(col1, text="S", variable=self.s_var, bg=self.bg_color, 
                               fg=self.text_color, selectcolor=self.bg_color, 
                               activebackground=self.bg_color, activeforeground=self.text_color)
        s_check.pack(anchor=tk.W)
        
        # Shift na coluna 1
        shift_check = tk.Checkbutton(col1, text="SHIFT", variable=self.shift_var, bg=self.bg_color, 
                                   fg=self.text_color, selectcolor=self.bg_color, 
                                   activebackground=self.bg_color, activeforeground=self.text_color)
        shift_check.pack(anchor=tk.W)
        
        # A na coluna 2
        a_check = tk.Checkbutton(col2, text="A", variable=self.a_var, bg=self.bg_color, 
                               fg=self.text_color, selectcolor=self.bg_color, 
                               activebackground=self.bg_color, activeforeground=self.text_color)
        a_check.pack(anchor=tk.W)
        
        # D na coluna 2
        d_check = tk.Checkbutton(col2, text="D", variable=self.d_var, bg=self.bg_color, 
                               fg=self.text_color, selectcolor=self.bg_color, 
                               activebackground=self.bg_color, activeforeground=self.text_color)
        d_check.pack(anchor=tk.W)
        
        # Opção de segurar para ativar na coluna 2
        hold_check = tk.Checkbutton(col2, text="Segurar para ativar", variable=self.hold_var, bg=self.bg_color, 
                                  fg=self.text_color, selectcolor=self.bg_color, 
                                  activebackground=self.bg_color, activeforeground=self.text_color)
        hold_check.pack(anchor=tk.W)
        
        # Nota sobre A e D abaixo dos checkboxes
        note = tk.Label(keys_frame, text="A e D juntos = alternância automática suave", bg=self.bg_color, fg="#ffaa00", font=("Arial", 8))
        note.pack(anchor=tk.W, pady=(5, 0))
        
        # Adicionar GIF do Myers abaixo do frame de teclas
        try:
            # Placeholder para o GIF - Carregará o gif real quando disponível
            self.myers_gif_label = tk.Label(left_frame, bg=self.bg_color)
            self.myers_gif_label.pack(pady=(10, 10))
            self.load_myers_gif()
        except Exception as e:
            print(f"Erro ao carregar o GIF: {e}")
            # Se não conseguir carregar o GIF, criar um espaço vazio
            empty_space = tk.Frame(left_frame, height=80, bg=self.bg_color)
            empty_space.pack(pady=(10, 10))
        
        # Área de gravação (invisível)
        self.recording_label = tk.Label(left_frame, text="Pressione qualquer tecla...", bg=self.bg_color, fg="orange")
        self.recording_label.pack(pady=(10, 0))
        self.recording_label.pack_forget()
        
        # Lado direito - Controles e Visualizador
        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame de controles
        controls_frame = tk.LabelFrame(right_frame, text="CONTROLES", bg=self.bg_color, fg=self.text_color, padx=10, pady=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid para os controles
        controls_grid = tk.Frame(controls_frame, bg=self.bg_color)
        controls_grid.pack(fill=tk.X)
        
        # Área de ativação
        activation_frame = tk.Frame(controls_grid, bg=self.bg_color)
        activation_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(activation_frame, text="Ativação:", bg=self.bg_color, fg=self.text_color, width=15, anchor='w').pack(side=tk.LEFT)
        
        self.activation_button = tk.Button(activation_frame, text=self.config["activation_key"], bg="#333333", 
                                        fg=self.text_color, width=10, command=lambda: self.start_recording("activation_key"))
        self.activation_button.pack(side=tk.LEFT)
        
        # Área de emergência
        emergency_frame = tk.Frame(controls_grid, bg=self.bg_color)
        emergency_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(emergency_frame, text="Emergência/Ligar:", bg=self.bg_color, fg=self.text_color, width=15, anchor='w').pack(side=tk.LEFT)
        
        self.emergency_button = tk.Button(emergency_frame, text=self.config["emergency_key"], bg="#333333", 
                                       fg=self.text_color, width=10, command=lambda: self.start_recording("emergency_key"))
        self.emergency_button.pack(side=tk.LEFT)
        
        # Área de Macro do Mouse
        mouse_macro_frame = tk.LabelFrame(controls_frame, text="Macro de Mouse", bg=self.bg_color, fg=self.text_color, padx=5, pady=5)
        mouse_macro_frame.pack(fill=tk.X, pady=5)
        
        # Checkbox para habilitar macro de mouse
        mouse_macro_check = tk.Checkbutton(mouse_macro_frame, text="Ativar macro de mouse", variable=self.mouse_macro_var, 
                                         bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                         activebackground=self.bg_color, activeforeground=self.text_color,
                                         command=self.toggle_mouse_macro)
        mouse_macro_check.pack(anchor=tk.W)
        
        # Botão de mouse para macro
        mouse_btn_frame = tk.Frame(mouse_macro_frame, bg=self.bg_color)
        mouse_btn_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(mouse_btn_frame, text="Botão:", bg=self.bg_color, fg=self.text_color, width=6, anchor='w').pack(side=tk.LEFT)
        
        self.mouse_btn_button = tk.Button(mouse_btn_frame, text=self.config["mouse_macro_button"], bg="#333333", 
                                       fg=self.text_color, width=10, command=lambda: self.start_recording("mouse_macro_button"))
        self.mouse_btn_button.pack(side=tk.LEFT)
        
        # Nova área para movimentação do mouse
        mouse_movement_frame = tk.LabelFrame(right_frame, text="MOVIMENTO DO MOUSE", bg=self.bg_color, fg=self.text_color, padx=5, pady=5)
        mouse_movement_frame.pack(fill=tk.X, pady=5)
        
        # Checkbox para habilitar movimento do mouse
        mouse_move_check = tk.Checkbutton(mouse_movement_frame, text="Ativar movimento do mouse", variable=self.mouse_movement_var, 
                                         bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                         activebackground=self.bg_color, activeforeground=self.text_color,
                                         command=self.toggle_mouse_movement)
        mouse_move_check.pack(anchor=tk.W)
        
        # Direção do movimento
        mouse_dir_frame = tk.Frame(mouse_movement_frame, bg=self.bg_color)
        mouse_dir_frame.pack(fill=tk.X, pady=3)
        
        # Opções de direção
        mouse_move_normal = tk.Radiobutton(mouse_dir_frame, text="Normal: A→Direita, D→Esquerda", 
                                          variable=self.mouse_movement_inverse_var, value=False,
                                          bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                          activebackground=self.bg_color, activeforeground=self.text_color,
                                          command=self.update_mouse_direction)
        mouse_move_normal.pack(anchor=tk.W)
        
        mouse_move_inverse = tk.Radiobutton(mouse_dir_frame, text="Inverso: A→Esquerda, D→Direita", 
                                           variable=self.mouse_movement_inverse_var, value=True,
                                           bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                           activebackground=self.bg_color, activeforeground=self.text_color,
                                           command=self.update_mouse_direction)
        mouse_move_inverse.pack(anchor=tk.W)
        
        # Visualizador de teclas
        keys_viz_frame = tk.LabelFrame(right_frame, text="TECLAS ATIVAS", bg=self.bg_color, fg=self.text_color, padx=10, pady=10)
        keys_viz_frame.pack(fill=tk.X, pady=(10, 10))
        
        # Layout mais compacto para o visualizador
        viz_grid = tk.Frame(keys_viz_frame, bg=self.bg_color)
        viz_grid.pack(fill=tk.X)
        
        # Botões do visualizador em uma única linha
        self.viz_w = tk.Button(viz_grid, text="W", bg=self.key_inactive_color, fg=self.text_color, width=4, state="disabled")
        self.viz_w.pack(side=tk.LEFT, padx=5)
        
        self.viz_a = tk.Button(viz_grid, text="A", bg=self.key_inactive_color, fg=self.text_color, width=4, state="disabled")
        self.viz_a.pack(side=tk.LEFT, padx=5)
        
        self.viz_s = tk.Button(viz_grid, text="S", bg=self.key_inactive_color, fg=self.text_color, width=4, state="disabled")
        self.viz_s.pack(side=tk.LEFT, padx=5)
        
        self.viz_d = tk.Button(viz_grid, text="D", bg=self.key_inactive_color, fg=self.text_color, width=4, state="disabled")
        self.viz_d.pack(side=tk.LEFT, padx=5)
        
        self.viz_shift = tk.Button(viz_grid, text="SHIFT", bg=self.key_inactive_color, fg=self.text_color, width=6, state="disabled")
        self.viz_shift.pack(side=tk.LEFT, padx=5)
        
        # Adicionar indicador de movimento do mouse
        mouse_move_indicator_frame = tk.Frame(right_frame, bg=self.bg_color)
        mouse_move_indicator_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.mouse_move_indicator = tk.Label(mouse_move_indicator_frame, text="Mouse: Inativo", bg=self.bg_color, fg="#aaaaaa")
        self.mouse_move_indicator.pack(anchor=tk.W)
        
        # Botão de ligar/desligar na parte inferior
        self.toggle_button = tk.Button(main_frame, text="INICIAR", bg="#00aa00", fg="white", 
                                     font=("Arial", 12, "bold"), height=2, command=self.toggle_script)
        self.toggle_button.pack(fill=tk.X, pady=(10, 0))
        
        # Informações
        info_frame = tk.Frame(main_frame, bg=self.bg_color)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "• F12 para ativar/desativar o script de qualquer lugar  •  Configurações são salvas automaticamente"
        info_label = tk.Label(info_frame, text=info_text, bg=self.bg_color, fg="#aaaaaa", font=("Arial", 8), justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

    def load_myers_gif(self):
        """Carrega o GIF do Myers se disponível"""
        try:
            if os.path.exists("myers.gif"):
                # Tentar carregar o GIF animado
                self.gif_frames = []
                self.current_frame = 0
                
                gif = Image.open("myers.gif")
                new_width, new_height = 200, 150  # Ajuste os valores como necessário
                try:
                    while True:
                        # Redimensiona cada quadro
                        gif_frame = gif.copy()
                        gif_frame = gif_frame.resize((new_width, new_height))  # Redimensiona o quadro
                        photoframe = ImageTk.PhotoImage(gif_frame)
                        self.gif_frames.append(photoframe)
                        gif.seek(gif.tell() + 1)
                except EOFError:
                    pass
                
                if self.gif_frames:
                    self.myers_gif_label.config(image=self.gif_frames[0])
                    self.animate_gif()
            else:
                # Se não encontrar o GIF, mostrar um placeholder
                placeholder = tk.Label(self.myers_gif_label, text="GIF do Myers\n(coloque myers.gif na pasta)", 
                                       bg=self.bg_color, fg=self.accent_color, height=4)
                placeholder.pack()
        except Exception as e:
            print(f"Erro ao processar o GIF: {e}")

    def animate_gif(self):
        """Anima o GIF do Myers"""
        if hasattr(self, 'gif_frames') and self.gif_frames:
            frame = self.gif_frames[self.current_frame]
            self.myers_gif_label.configure(image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.root.after(100, self.animate_gif)  # Atualiza a cada 100ms
    
    def toggle_mouse_macro(self):
        # Atualizar configuração
        self.config["mouse_macro_enabled"] = self.mouse_macro_var.get()
        # Salvar configuração
        self.save_config()
    
    def toggle_mouse_movement(self):
        # Atualizar configuração
        self.config["mouse_movement_enabled"] = self.mouse_movement_var.get()
        # Salvar configuração
        self.save_config()
    
    def update_mouse_direction(self):
        # Atualizar configuração
        self.config["mouse_movement_inverse"] = self.mouse_movement_inverse_var.get()
        # Salvar configuração
        self.save_config()

    def start_emergency_listener(self):
        # Configurar listener para a tecla de emergência (que também serve para ligar)
        # Este listener fica ativo o tempo todo, mesmo com o script desligado
        self.emergency_listener = keyboard.Listener(on_press=self.on_emergency_key)
        self.emergency_listener.daemon = True
        self.emergency_listener.start()

    def on_emergency_key(self, key):
        # Obter nome da tecla
        key_name = ""
        try:
            if hasattr(key, 'char') and key.char:
                key_name = key.char.lower()
            else:
                key_name = str(key).replace('Key.', '')
                
            # Se for a tecla de emergência
            if key_name == self.config["emergency_key"]:
                # Se o script estiver rodando, desligar
                if self.running:
                    self.stop_script()
                # Se o script estiver desligado, ligar
                else:
                    self.start_script()
        except:
            pass

    def start_recording(self, target):
        if self.running:
            tk.messagebox.showinfo("Aviso", "Pare o script antes de alterar controles.")
            return
            
        self.recording = True
        self.record_target = target
        
        # Mostrar instrução
        self.recording_label.config(text="Pressione qualquer tecla ou botão...")
        self.recording_label.pack(pady=(10, 0))
        
        # Desabilitar botões
        self.activation_button.config(state="disabled")
        self.emergency_button.config(state="disabled")
        self.mouse_btn_button.config(state="disabled")
        
        # Configurar listener temporário
        listener = keyboard.Listener(on_press=self.on_record_key)
        listener.start()
        
        # Para qualquer target, registrar também clique do mouse
        mouse_listener = mouse.Listener(on_click=self.on_record_mouse)
        mouse_listener.start()

    def on_record_key(self, key):
        if not self.recording:
            return
            
        # Obter nome da tecla
        key_name = ""
        try:
            if hasattr(key, 'char') and key.char:
                key_name = key.char.lower()
            else:
                key_name = str(key).replace('Key.', '')
        except:
            key_name = str(key).replace('Key.', '')
            
        # Atualizar configuração
        self.config[self.record_target] = key_name
        
        # Atualizar botão
        if self.record_target == "activation_key":
            self.activation_button.config(text=key_name)
        elif self.record_target == "emergency_key":
            self.emergency_button.config(text=key_name)
        elif self.record_target == "mouse_macro_button":
            self.mouse_btn_button.config(text=key_name)
            
        # Encerrar gravação
        self.finish_recording()
        
        # Salvar configuração
        self.save_config()
        
        return False  # Parar o listener

    def on_record_mouse(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return False
            
        # Mapear botão do mouse
        button_name = str(button).replace('Button.', '')
        
        # Atualizar configuração
        self.config[self.record_target] = button_name
        
        # Atualizar botão
        if self.record_target == "activation_key":
            self.activation_button.config(text=button_name)
        elif self.record_target == "mouse_macro_button":
            self.mouse_btn_button.config(text=button_name)
            
        # Encerrar gravação
        self.finish_recording()
        
        # Salvar configuração
        self.save_config()
        
        return False  # Parar o listener

    def finish_recording(self):
        self.recording = False
        self.record_target = None
        
        # Esconder instrução
        self.recording_label.pack_forget()
        
        # Reabilitar botões
        self.activation_button.config(state="normal")
        self.emergency_button.config(state="normal")
        self.mouse_btn_button.config(state="normal")

    def toggle_script(self):
        if not self.running:
            self.start_script()
        else:
            self.stop_script()

    def start_script(self):
        # Atualizar configuração com estado das checkboxes
        self.config["w_active"] = self.w_var.get()
        self.config["s_active"] = self.s_var.get()
        self.config["shift_active"] = self.shift_var.get()
        self.config["a_active"] = self.a_var.get()
        self.config["d_active"] = self.d_var.get()
        self.config["hold_to_activate"] = self.hold_var.get()
        self.config["mouse_macro_enabled"] = self.mouse_macro_var.get()
        self.config["mouse_movement_enabled"] = self.mouse_movement_var.get()
        self.config["mouse_movement_inverse"] = self.mouse_movement_inverse_var.get()
        
        # Salvar configuração
        self.save_config()
        
        # Iniciar thread de teclas
        self.running = True
        self.key_thread = threading.Thread(target=self.key_loop)
        self.key_thread.daemon = True
        self.key_thread.start()
        
        # Iniciar listeners
        self.setup_listeners()
        
        # Atualizar interface
        self.status_text.config(text="INICIADO", fg="blue")
        self.toggle_button.config(text="PARAR", bg="#aa0000")
        
        # Desabilitar controles
        self.activation_button.config(state="disabled")
        self.emergency_button.config(state="disabled")
        self.mouse_btn_button.config(state="disabled")
        
        # Mostrar teclas ativas
        active_keys = []
        if self.config["w_active"]: active_keys.append("W")
        if self.config["s_active"]: active_keys.append("S")
        if self.config["shift_active"]: active_keys.append("SHIFT")
        if self.config["a_active"]: active_keys.append("A")
        if self.config["d_active"]: active_keys.append("D")
        
        # Texto do modo de ativação
        activation_mode = "Segurar para ativar" if self.config["hold_to_activate"] else "Alternar para ativar"
        
        # Texto da macro e movimento do mouse
        macro_text = ""
        if self.config["mouse_macro_enabled"]:
            macro_text = f"\nMacro de mouse ativada: {self.config['mouse_macro_button']}"
            
        mouse_move_text = ""
        if self.config["mouse_movement_enabled"]:
            if self.config["mouse_movement_inverse"]:
                mouse_move_text = "\nMovimento do mouse: A→Esquerda, D→Direita"
            else:
                mouse_move_text = "\nMovimento do mouse: A→Direita, D→Esquerda"
        
        tk.messagebox.showinfo("Iniciado", 
            f"Script iniciado!\n\n"
            f"Teclas ativas: {', '.join(active_keys) if active_keys else 'Nenhuma'}\n"
            f"Modo: {activation_mode}\n"
            f"Use {self.config['activation_key']} para ativar/desativar\n"
            f"Pressione {self.config['emergency_key']} para ligar/desligar"
            f"{macro_text}"
            f"{mouse_move_text}")

    def stop_script(self):
        # Parar script
        self.running = False
        self.moonwalk_active = False
        
        # Parar listeners
        if self.key_listener:
            self.key_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # Liberar teclas
        self.release_keys()
        
        # Atualizar interface
        self.status_text.config(text="DESATIVADO", fg="red")
        self.toggle_button.config(text="INICIAR", bg="#00aa00")
        self.mouse_move_indicator.config(text="Mouse: Inativo", fg="#aaaaaa")
        
        # Reabilitar controles
        self.activation_button.config(state="normal")
        self.emergency_button.config(state="normal")
        self.mouse_btn_button.config(state="normal")
        
        # Redefinir visualizador de teclas
        self.update_key_viz('w', False)
        self.update_key_viz('s', False)
        self.update_key_viz('shift', False)
        self.update_key_viz('a', False)
        self.update_key_viz('d', False)

    def setup_listeners(self):
        # Listener de teclado
        self.key_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.key_listener.start()
        
        # Listener de mouse
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def on_key_press(self, key):
        if not self.running:
            return
            
        # Verificar tecla de ativação
        activation_key = self.config["activation_key"]
        
        try:
            # Verificar se é a tecla de ativação
            key_name = ""
            if hasattr(key, 'char') and key.char:
                key_name = key.char.lower()
            else:
                key_name = str(key).replace('Key.', '')
                
            # Tecla de ativação no modo "segurar"
            if key_name == activation_key and self.config["hold_to_activate"]:
                self.moonwalk_active = True
                self.status_text.config(text="MOONWALK ATIVO", fg="green")
            # Tecla de ativação no modo "alternar"
            elif key_name == activation_key and not self.config["hold_to_activate"]:
                self.toggle_moonwalk()
        except:
            pass

    def on_key_release(self, key):
        if not self.running:
            return
            
        # Verificar tecla de ativação para modo "segurar"
        activation_key = self.config["activation_key"]
        
        try:
            # Obter nome da tecla
            key_name = ""
            if hasattr(key, 'char') and key.char:
                key_name = key.char.lower()
            else:
                key_name = str(key).replace('Key.', '')
                
            # Desativar moonwalk quando soltar a tecla no modo "segurar"
            if key_name == activation_key and self.config["hold_to_activate"] and self.moonwalk_active:
                self.moonwalk_active = False
                self.status_text.config(text="INICIADO", fg="blue")
                self.release_keys()
                self.mouse_move_indicator.config(text="Mouse: Inativo", fg="#aaaaaa")
        except:
            pass

    def on_mouse_click(self, x, y, button, pressed):
        if not self.running:
            return
            
        # Verificar se é o botão de ativação
        button_name = str(button).replace('Button.', '')
        
        # Botão de ativação
        if button_name == self.config["activation_key"]:
            # No modo segurar, ativar ao pressionar e desativar ao soltar
            if self.config["hold_to_activate"]:
                if pressed:
                    self.moonwalk_active = True
                    self.status_text.config(text="MOONWALK ATIVO", fg="green")
                else:
                    self.moonwalk_active = False
                    self.status_text.config(text="INICIADO", fg="blue")
                    self.release_keys()
                    self.mouse_move_indicator.config(text="Mouse: Inativo", fg="#aaaaaa")
            # No modo alternar, mudar o estado ao pressionar
            elif pressed:
                self.toggle_moonwalk()
        
        # Verificar macro de mouse
        if self.config["mouse_macro_enabled"] and button_name == self.config["mouse_macro_button"] and pressed:
            # Simular o pressionamento da tecla de ativação
            if self.config["hold_to_activate"]:
                self.moonwalk_active = True
                self.status_text.config(text="MOONWALK ATIVO", fg="green")
            else:
                self.toggle_moonwalk()

    def toggle_moonwalk(self):
        # Alternar estado
        self.moonwalk_active = not self.moonwalk_active
        
        # Reiniciar contador A/D
        self.ad_counter = 0
        self.ad_last_time = time.time()
        
        # Reiniciar movimento do mouse
        self.last_mouse_move_time = time.time()
        
        # Atualizar interface
        if self.moonwalk_active:
            self.status_text.config(text="MOONWALK ATIVO", fg="green")
            if self.config["mouse_movement_enabled"]:
                self.mouse_move_indicator.config(text="Mouse: Pronto para mover", fg="#ffaa00")
        else:
            self.status_text.config(text="INICIADO", fg="blue")
            self.mouse_move_indicator.config(text="Mouse: Inativo", fg="#aaaaaa")
            # Liberar todas as teclas quando desativado
            self.release_keys()

    def move_mouse(self, direction):
        """Move o mouse com base na direção (esquerda ou direita)"""
        if not self.config["mouse_movement_enabled"] or not self.moonwalk_active:
            return
            
        current_time = time.time()
        if current_time - self.last_mouse_move_time < self.mouse_move_delay:
            return
        
        self.last_mouse_move_time = current_time
        
        if direction == 'left':
            self.mouse.move(-self.mouse_move_amount, 0)
            self.mouse_move_indicator.config(text="Mouse: Movendo ← Esquerda", fg="#00aaff")
        elif direction == 'right':
            self.mouse.move(self.mouse_move_amount, 0)
            self.mouse_move_indicator.config(text="Mouse: Movendo → Direita", fg="#00aaff")

    def key_loop(self):
        while self.running:
            if self.moonwalk_active:
                # Controle de teclas W, S com pressão mais precisa
                if self.config["w_active"]:
                    self.press_key_precise('w')
                    self.update_key_viz('w', True)
                if self.config["s_active"]:
                    self.press_key_precise('s')
                    self.update_key_viz('s', True)
                    
                # Controle de Shift
                if self.config["shift_active"]:
                    self.press_key_precise('shift')
                    self.update_key_viz('shift', True)
                    
                # Controle de A e D
                a_active = self.config["a_active"]
                d_active = self.config["d_active"]
                
                # Se ambos A e D estão ativos, alternar com timing mais preciso
                if a_active and d_active:
                    current_time = time.time()
                    # Adicionar variação aleatória mínima ao intervalo para maior precisão
                    interval = self.ad_interval + random.uniform(-0.005, 0.005)
                    
                    if current_time - self.ad_last_time >= interval:
                        # Tempo para a próxima alternância
                        self.ad_last_time = current_time
                        
                        # Liberar ambas as teclas com precisão
                        self.release_key_precise('a')
                        self.release_key_precise('d')
                        self.update_key_viz('a', False)
                        self.update_key_viz('d', False)
                        
                        # Esperar um tempo mínimo entre soltar uma tecla e pressionar outra
                        # Esse tempo de transição é menor para maior precisão
                        transition_time = self.ad_transition_time + random.uniform(0, 0.005)
                        time.sleep(transition_time)
                        
                        # Pressionar alternadamente com maior precisão
                        if self.ad_counter % 2 == 0:
                            self.press_key_precise('a')
                            self.update_key_viz('a', True)
                            
                            # Mover mouse com base na tecla A
                            if self.config["mouse_movement_inverse"]:
                                self.move_mouse('left')  # Inverso: A move para esquerda
                            else:
                                self.move_mouse('right')  # Normal: A move para direita
                        else:
                            self.press_key_precise('d')
                            self.update_key_viz('d', True)
                            
                            # Mover mouse com base na tecla D
                            if self.config["mouse_movement_inverse"]:
                                self.move_mouse('right')  # Inverso: D move para direita
                            else:
                                self.move_mouse('left')  # Normal: D move para esquerda
                            
                        self.ad_counter += 1
                else:
                    # Pressionar individualmente com maior precisão
                    if a_active:
                        self.press_key_precise('a')
                        self.update_key_viz('a', True)
                        
                        # Mover mouse com base na tecla A (quando pressionada individualmente)
                        if self.config["mouse_movement_enabled"]:
                            if self.config["mouse_movement_inverse"]:
                                self.move_mouse('left')  # Inverso: A move para esquerda
                            else:
                                self.move_mouse('right')  # Normal: A move para direita
                                
                    if d_active:
                        self.press_key_precise('d')
                        self.update_key_viz('d', True)
                        
                        # Mover mouse com base na tecla D (quando pressionada individualmente)
                        if self.config["mouse_movement_enabled"]:
                            if self.config["mouse_movement_inverse"]:
                                self.move_mouse('right')  # Inverso: D move para direita
                            else:
                                self.move_mouse('left')  # Normal: D move para esquerda
            else:
                # Quando não estiver ativo, garantir que todas as teclas foram liberadas
                self.release_keys()
                
                # Atualizar o visualizador para mostrar teclas inativas
                self.update_key_viz('w', False)
                self.update_key_viz('s', False)
                self.update_key_viz('shift', False)
                self.update_key_viz('a', False)
                self.update_key_viz('d', False)
                
                # Atualizar indicador de movimento do mouse
                self.mouse_move_indicator.config(text="Mouse: Inativo", fg="#aaaaaa")
            
            # Pausa mínima para diminuir uso de CPU e garantir precisão
            time.sleep(0.005)

    def update_key_viz(self, key, active):
        # Não fazer nada se o estado não mudar
        if self.key_states.get(key) == active:
            return
            
        # Atualizar estado
        self.key_states[key] = active
        
        # Atualizar visualizador
        try:
            if key == 'w':
                color = self.key_active_color if active else self.key_inactive_color
                self.viz_w.config(bg=color)
            elif key == 's':
                color = self.key_active_color if active else self.key_inactive_color
                self.viz_s.config(bg=color)
            elif key == 'a':
                color = self.key_active_color if active else self.key_inactive_color
                self.viz_a.config(bg=color)
            elif key == 'd':
                color = self.key_active_color if active else self.key_inactive_color
                self.viz_d.config(bg=color)
            elif key == 'shift':
                color = self.key_active_color if active else self.key_inactive_color
                self.viz_shift.config(bg=color)
        except:
            pass  # Ignorar erros de atualização de UI

    def press_key_precise(self, key):
        """Versão mais precisa do press_key que usa menos recursos do sistema"""
        try:
            if not self.key_states.get(key, False):  # Verificar se a tecla já está pressionada
                if key == 'shift':
                    self.keyboard.press(Key.shift)
                elif key == 'ctrl':
                    self.keyboard.press(Key.ctrl)
                elif key == 'alt':
                    self.keyboard.press(Key.alt)
                elif key == 'space':
                    self.keyboard.press(Key.space)
                elif len(key) == 1:
                    self.keyboard.press(key)
                self.key_states[key] = True
        except Exception as e:
            print(f"Erro ao pressionar {key}: {e}")

    def release_key_precise(self, key):
        """Versão mais precisa do release_key que usa menos recursos do sistema"""
        try:
            if self.key_states.get(key, False):  # Verificar se a tecla está pressionada
                if key == 'shift':
                    self.keyboard.release(Key.shift)
                elif key == 'ctrl':
                    self.keyboard.release(Key.ctrl)
                elif key == 'alt':
                    self.keyboard.release(Key.alt)
                elif key == 'space':
                    self.keyboard.release(Key.space)
                elif len(key) == 1:
                    self.keyboard.release(key)
                self.key_states[key] = False
        except Exception as e:
            print(f"Erro ao liberar {key}: {e}")

    def press_key(self, key):
        """Método antigo mantido para compatibilidade"""
        self.press_key_precise(key)

    def release_key(self, key):
        """Método antigo mantido para compatibilidade"""
        self.release_key_precise(key)

    def release_keys(self):
        # Liberar todas as teclas, independente se estão configuradas como ativas
        # Isso garante que o teclado fique livre quando o moonwalk não está ativo
        for key in ['w', 's', 'a', 'd', 'shift']:
            self.release_key_precise(key)
            self.update_key_viz(key, False)

    def save_config(self):
        try:
            with open("dbd_config.json", "w") as file:
                json.dump(self.config, file)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def load_config(self):
        try:
            if os.path.exists("dbd_config.json"):
                with open("dbd_config.json", "r") as file:
                    loaded_config = json.load(file)
                    # Atualizar apenas as chaves que existem
                    for key in self.config:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            # Se houver erro, manter as configurações padrão

    def on_close(self):
        if self.running:
            self.stop_script()
            
        # Parar listener de emergência
        if self.emergency_listener:
            self.emergency_listener.stop()
            
        # Garantir que todas as teclas estão livres
        self.release_keys()
        
        # Salvar configurações
        self.save_config()
        
        # Fechar janela
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# Iniciar o aplicativo
if __name__ == "__main__":
    app = DBDMoonwalk()
    app.run()