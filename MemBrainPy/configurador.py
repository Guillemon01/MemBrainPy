import tkinter as tk
from tkinter import ttk, messagebox
import re
import random
from .SistemaP import SistemaP, Membrana, Regla

class ConfiguradorPSistema(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configurador de Sistema P")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")
        # Estilos
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabelFrame', background='#e8e8e8', font=('Arial', 10, 'bold'))
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 9))
        self.style.configure('TButton', font=('Arial', 9))
        self.style.configure('Treeview', font=('Consolas', 10), rowheight=24)

        self.system = None
        self.selected_membrane = None
        self.mem_counter = 0
        self.saved = False  # bandera para indicar guardado
        self.exit_membrane_id = None  # id de membrana de salida

        # Manejar cierre de ventana
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self._construir_interfaz()
        # Generar sistema inicial vacío
        self.generar_sistema_aleatorio()

    def _on_close(self):
        self.saved = False
        self.destroy()

    def _construir_interfaz(self):
        cont = ttk.Frame(self)
        cont.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=2)
        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(0, weight=1)

        # Árbol de membranas
        tree_frame = ttk.LabelFrame(cont, text='Estructura de Membranas')
        tree_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame)
        self.tree.heading('#0', text='Membranas')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.grid(row=0, column=0, rowspan=3, sticky='nsew', padx=5, pady=5)
        self.var_salida = tk.BooleanVar()
        self.chk_salida = ttk.Checkbutton(tree_frame, text='Membrana de salida', variable=self.var_salida,
                                         command=self._on_toggle_salida)
        self.chk_salida.grid(row=1, column=0, sticky='w', padx=5, pady=(0,5))

        # Recursos
        res_frame = ttk.LabelFrame(cont, text='Recursos')
        res_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        res_frame.columnconfigure(1, weight=1)
        ttk.Label(res_frame, text='Símbolos (letras):').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.entry_simbolo = ttk.Entry(res_frame)
        self.entry_simbolo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(res_frame, text='Añadir recurso', command=self.agregar_recurso).grid(row=0, column=2, padx=5)
        self.lista_recursos = tk.Listbox(res_frame, height=5, font=('Consolas', 10))
        self.lista_recursos.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=5)

        # Definición de reglas
        regla_frame = ttk.LabelFrame(cont, text='Definición de Reglas')
        regla_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        for i in range(3): regla_frame.columnconfigure(i, weight=1)
        ttk.Label(regla_frame, text='Consumir*:').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.entry_izq = ttk.Entry(regla_frame)
        self.entry_izq.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(regla_frame, text='Producir:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.entry_der = ttk.Entry(regla_frame)
        self.entry_der.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(regla_frame, text='Prioridad:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        vcmd = (self.register(self._validate_entero), '%P')
        self.entry_prioridad = ttk.Entry(regla_frame, validate='key', validatecommand=vcmd)
        self.entry_prioridad.insert(0, '1')
        self.entry_prioridad.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        self.var_disolver = tk.BooleanVar()
        self.var_crear = tk.BooleanVar()
        ttk.Checkbutton(regla_frame, text='Disolver membrana', variable=self.var_disolver,
                        command=self._toggle_options).grid(row=3, column=0, sticky='w', padx=5)
        ttk.Checkbutton(regla_frame, text='Crear membrana', variable=self.var_crear,
                        command=self._toggle_options).grid(row=4, column=0, sticky='w', padx=5)
        ttk.Label(regla_frame, text='ID destino:').grid(row=4, column=1, sticky='e', padx=5)
        self.entry_crear = ttk.Entry(regla_frame, width=5, state='disabled')
        self.entry_crear.grid(row=4, column=2, sticky='w', padx=5)
        ttk.Button(regla_frame, text='Añadir regla', command=self.agregar_regla).grid(row=5, column=0, columnspan=3, pady=10)
        self.lbl_status = ttk.Label(regla_frame, text='', font=('Arial', 9, 'italic'))
        self.lbl_status.grid(row=6, column=0, columnspan=3, pady=(0,10))

        # Lista de reglas
        reglas_frame = ttk.LabelFrame(cont, text='Reglas de la Membrana Seleccionada')
        reglas_frame.grid(row=1, column=0, columnspan=1, sticky='nsew', padx=5, pady=5)
        reglas_frame.columnconfigure(0, weight=1)
        self.lista_reglas = tk.Listbox(reglas_frame, height=6, font=('Consolas',10))
        self.lista_reglas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Panel inferior: agregar membrana, generar aleatorio y guardar
        bottom = ttk.Frame(self)
        bottom.pack(side='bottom', fill='x', padx=10, pady=5)
        ttk.Label(bottom, text='ID Padre para nueva membrana:').pack(side='left', padx=5)
        self.entry_padre = ttk.Entry(bottom, width=5)
        self.entry_padre.pack(side='left')
        ttk.Button(bottom, text='Agregar membrana', command=self.agregar_membrana).pack(side='left', padx=5)
        ttk.Button(bottom, text='Generar aleatorio', command=self.generar_sistema_aleatorio).pack(side='left', padx=5)
        ttk.Button(bottom, text='Guardar y salir', command=self.on_save).pack(side='right', padx=10)

    def _validate_entero(self, v):
        return v.isdigit() or v == ''

    def _toggle_options(self):
        if self.var_disolver.get():
            self.var_crear.set(False)
            self.entry_crear.configure(state='disabled')
        elif self.var_crear.get():
            self.var_disolver.set(False)
            self.entry_crear.configure(state='normal')
        else:
            self.entry_crear.configure(state='disabled')

    def _texto_membrana(self, m: Membrana) -> str:
        if m.resources:
            s = ','.join(f"{k}:{v}" for k,v in sorted(m.resources.items()))
            base = f"Membrana {m.id_mem} [{s}]"
        else:
            base = f"Membrana {m.id_mem} []"
        if self.exit_membrane_id == m.id_mem:
            return base + " (SALIDA)"
        return base

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_membrane = self.system.skin[sel[0]]
            self._actualizar_recursos()
            self._actualizar_reglas()
            self.var_salida.set(self.selected_membrane.id_mem == self.exit_membrane_id)
        for mem_id, membr in self.system.skin.items():
            self.tree.item(mem_id, text=self._texto_membrana(membr))

    def _on_toggle_salida(self):
        if not self.selected_membrane:
            return
        prev = self.exit_membrane_id
        if prev:
            node_prev = self.system.skin.get(prev)
            if node_prev:
                self.tree.item(prev, text=self._texto_membrana(node_prev))
        if self.var_salida.get():
            self.exit_membrane_id = self.selected_membrane.id_mem
        else:
            self.exit_membrane_id = None
        self.system.output_membrane = self.exit_membrane_id
        for mem_id, membr in self.system.skin.items():
            self.tree.item(mem_id, text=self._texto_membrana(membr))

    def _actualizar_recursos(self):
        self.lista_recursos.delete(0, 'end')
        for k,v in sorted(self.selected_membrane.resources.items()):
            self.lista_recursos.insert('end', f"{k}: {v}")
        self.tree.item(self.selected_membrane.id_mem, text=self._texto_membrana(self.selected_membrane))

    def _actualizar_reglas(self):
        self.lista_reglas.delete(0, 'end')
        for r in self.selected_membrane.reglas:
            parts = []
            consumir = ' '.join(f"{sym}×{cnt}" for sym,cnt in r.left.items())
            parts.append(f"Consumir: {consumir}")
            if r.right:
                produzir = ' '.join(f"{sym}×{cnt}" for sym,cnt in r.right.items())
                parts.append(f"Producir: {produzir}")
            parts.append(f"Prioridad: {r.priority}")
            texto = ' | '.join(parts)
            self.lista_reglas.insert('end', texto)

    def agregar_membrana(self):
        pid = self.entry_padre.get().strip()
        self.mem_counter += 1
        nid = str(self.mem_counter)
        nueva = Membrana(id_mem=nid, resources={})
        if pid and pid in self.system.skin:
            self.system.add_membrane(nueva, pid)
            self.tree.insert(pid, 'end', nid, text=self._texto_membrana(nueva))
        elif self.selected_membrane:
            self.system.add_membrane(nueva, self.selected_membrane.id_mem)
            self.tree.insert(self.selected_membrane.id_mem, 'end', nid, text=self._texto_membrana(nueva))
        else:
            self.system.add_membrane(nueva, None)
            self.tree.insert('', 'end', nid, text=self._texto_membrana(nueva))
        self.entry_padre.delete(0, 'end')

    def agregar_recurso(self):
        if not self.selected_membrane:
            messagebox.showwarning('Advertencia', 'Seleccione una membrana antes de añadir recursos.')
            return
        s = self.entry_simbolo.get().strip()
        if not re.fullmatch(r'[A-Za-z]+', s):
            messagebox.showerror('Error', 'Símbolos ASCII sin acentos.')
            return
        for c in s:
            self.selected_membrane.resources[c] = self.selected_membrane.resources.get(c, 0) + 1
        self._actualizar_recursos()
        self.entry_simbolo.delete(0, 'end')

    def agregar_regla(self):
        izq = self.entry_izq.get().strip()
        if self.var_disolver.get() and self.selected_membrane and self.selected_membrane.id_mem == '1':
            messagebox.showerror('Error', 'No se puede disolver la membrana 1 (piel).')
            return
        if not re.fullmatch(r'[A-Za-z]+', izq):
            messagebox.showerror('Error', 'Campo consumir obligatorio.')
            return
        der = self.entry_der.get().strip()
        if der and not re.fullmatch(r'[A-Za-z]+', der):
            messagebox.showerror('Error', 'Campo producir inválido.')
            return
        prio = self.entry_prioridad.get().strip()
        if not prio:
            messagebox.showerror('Error', 'Prioridad obligatoria.')
            return
        regla = Regla(left=self._parsear(izq), right=self._parsear(der) if der else {}, priority=int(prio))
        self.selected_membrane.add_regla(regla)
        self.lbl_status.config(text='Regla añadida correctamente', foreground='green')
        self._actualizar_reglas()
        for e in (self.entry_izq, self.entry_der, self.entry_prioridad): e.delete(0, 'end')
        self.entry_prioridad.insert(0, '1')
        self.var_disolver.set(False);
        self.var_crear.set(False);
        self.entry_crear.delete(0, 'end');
        self.entry_crear.configure(state='disabled')

    def generar_sistema_aleatorio(self):
        # Inicializar nuevo sistema y árbol
        self.system = SistemaP()
        self.tree.delete(*self.tree.get_children())
        self.mem_counter = 0
        letras = list("abcdefghijk")
        # Número aleatorio de membranas
        total = random.randint(2,6)
        ids = []
        for _ in range(total):
            self.mem_counter += 1
            mid = str(self.mem_counter)
            m = Membrana(id_mem=mid, resources={})
            if ids:
                parent = random.choice(ids)
            else:
                parent = None
            self.system.add_membrane(m, parent)
            if parent:
                self.tree.insert(parent, 'end', mid, text=self._texto_membrana(m))
            else:
                self.tree.insert('', 'end', mid, text=self._texto_membrana(m))
            ids.append(mid)
            # Recursos aleatorios
            for _ in range(random.randint(0,10)):
                simbolo = random.choice(letras)
                m.resources[simbolo] = m.resources.get(simbolo,0) + 1
            # Reglas aleatorias
            num_reglas = random.randint(1,5)
            for __ in range(num_reglas):
                # Seleccionar consumo
                tipos_consumo = random.sample(letras, k=random.randint(1, min(3,len(letras))))
                left = {t: random.randint(1,3) for t in tipos_consumo}
                # Seleccionar producción
                prod_count = random.randint(0,3)
                tipos_prod = random.sample(letras, k=min(prod_count,len(letras)))
                right = {t: random.randint(1,3) for t in tipos_prod}
                r = Regla(left=left, right=right, priority=random.randint(1,5))
                m.add_regla(r)
        # Membrana de salida aleatoria
        self.exit_membrane_id = random.choice(ids)
        self.system.output_membrane = self.exit_membrane_id
        # Refrescar árbol
        for mem_id, membr in self.system.skin.items():
            self.tree.item(mem_id, text=self._texto_membrana(membr))
        # Seleccionar la raíz
        if ids:
            root = ids[0]
            self.tree.selection_set(root)
            self.on_select(None)

    def _parsear(self, s: str) -> dict:
        ms = {}
        for c in s:
            ms[c] = ms.get(c, 0) + 1
        return ms

    def on_save(self):
        self.saved = True
        self.destroy()


def configurar_sistema_p():
    app = ConfiguradorPSistema()
    app.mainloop()
    return app.system if app.saved else None

if __name__ == '__main__':
    sistema = configurar_sistema_p()
    print(sistema)
