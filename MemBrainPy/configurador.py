import tkinter as tk
from tkinter import ttk, messagebox
import re
from SistemaP import SistemaP, Membrana, Regla

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

        self.system = SistemaP()
        self.selected_membrane = None
        self.mem_counter = 1
        self.saved = False  # bandera para saber si guardó

        # Manejar cierre de ventana
        self.protocol('WM_DELETE_WINDOW', self._on_close)

        self._construir_interfaz()

    def _on_close(self):
        # Si cierra sin guardar, marcamos sin guardar y destruimos
        self.saved = False
        self.destroy()

    def _construir_interfaz(self):
        cont = ttk.Frame(self)
        cont.pack(fill='both', expand=True, padx=10, pady=10)
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
        self.tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Panel derecho: recursos + reglas definition
        right = ttk.LabelFrame(cont, text='Recursos y Definición de Reglas')
        right.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        for i in range(3): right.columnconfigure(i, weight=1)

        # Recursos
        ttk.Label(right, text='Símbolos (letras):').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.entry_simbolo = ttk.Entry(right)
        self.entry_simbolo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(right, text='Añadir recurso', command=self.agregar_recurso).grid(row=0, column=2, padx=5)
        self.lista_recursos = tk.Listbox(right, height=5, font=('Consolas',10))
        self.lista_recursos.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=5)

        # Separador
        ttk.Separator(right, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)

        # Definición de regla
        ttk.Label(right, text='Consumir*:').grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.entry_izq = ttk.Entry(right)
        self.entry_izq.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(right, text='Producir:').grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.entry_der = ttk.Entry(right)
        self.entry_der.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(right, text='Prioridad:').grid(row=5, column=0, sticky='e', padx=5, pady=2)
        vcmd = (self.register(self._validate_entero), '%P')
        self.entry_prioridad = ttk.Entry(right, validate='key', validatecommand=vcmd)
        self.entry_prioridad.insert(0, '1')
        self.entry_prioridad.grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        # Opciones de regla
        self.var_disolver = tk.BooleanVar()
        self.var_crear = tk.BooleanVar()
        ttk.Checkbutton(right, text='Disolver membrana', variable=self.var_disolver,
                        command=self._toggle_options).grid(row=6, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(right, text='Crear membrana', variable=self.var_crear,
                        command=self._toggle_options).grid(row=7, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(right, text='ID destino:').grid(row=7, column=1, sticky='e', padx=5)
        self.entry_crear = ttk.Entry(right, width=5, state='disabled')
        self.entry_crear.grid(row=7, column=2, sticky='w', padx=5)

        # Botón y estado
        ttk.Button(right, text='Añadir regla', command=self.agregar_regla).grid(row=8, column=0, columnspan=3, pady=10)
        self.lbl_status = ttk.Label(right, text='', font=('Arial', 9, 'italic'))
        self.lbl_status.grid(row=9, column=0, columnspan=3, pady=(0,10))

        # Lista de reglas
        reglas_frame = ttk.LabelFrame(cont, text='Reglas de la Membrana Seleccionada')
        reglas_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        reglas_frame.columnconfigure(0, weight=1)
        self.lista_reglas = tk.Listbox(reglas_frame, height=6, font=('Consolas',10))
        self.lista_reglas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Panel inferior: agregar membrana y guardar
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', pady=5)
        ttk.Label(bottom, text='ID Padre para nueva membrana:').pack(side='left', padx=5)
        self.entry_padre = ttk.Entry(bottom, width=5)
        self.entry_padre.pack(side='left')
        ttk.Button(bottom, text='Agregar membrana', command=self.agregar_membrana).pack(side='left', padx=5)
        ttk.Button(bottom, text='Guardar y salir', command=self.on_save).pack(side='right', padx=10)

        # Inicializar membrana raíz
        piel = Membrana(id_mem=str(self.mem_counter), resources={})
        self.system.add_membrane(piel, None)
        self.tree.insert('', 'end', str(self.mem_counter), text=self._texto_membrana(piel))

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
            return f"Membrana {m.id_mem} [{s}]"
        return f"Membrana {m.id_mem} []"

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_membrane = self.system.skin[sel[0]]
            self._actualizar_recursos()
            self._actualizar_reglas()

    def _actualizar_recursos(self):
        self.lista_recursos.delete(0, 'end')
        for k,v in sorted(self.selected_membrane.resources.items()):
            self.lista_recursos.insert('end', f"{k}: {v}")
        self.tree.item(self.selected_membrane.id_mem, text=self._texto_membrana(self.selected_membrane))

    def _actualizar_reglas(self):
        self.lista_reglas.delete(0, 'end')
        # Formatear cada regla para mostrar detalles
        for r in self.selected_membrane.reglas:
            parts = []
            # Consumir
            consumir = ' '.join(f"{sym}×{cnt}" for sym,cnt in r.left.items())
            parts.append(f"Consumir: {consumir}")
            # Producir
            if r.right:
                producir = ' '.join(f"{sym}×{cnt}" for sym,cnt in r.right.items())
                parts.append(f"Producir: {producir}")
            # Prioridad
            parts.append(f"Prioridad: {r.priority}")
            # Disolver
            if getattr(r, 'dissolve_membranes', []):
                parts.append(f"Disuelve: {', '.join(r.dissolve_membranes)}")
            # Crear
            if getattr(r, 'create_membranes', []):
                parts.append(f"Crea: {', '.join(r.create_membranes)}")
            # Juntar y mostrar
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
        s = self.entry_simbolo.get().strip()
        if not re.fullmatch(r'[A-Za-z]+', s):
            messagebox.showerror('Error', 'Símbolos ASCII sin acentos.')
            return
        for c in s:
            self.selected_membrane.resources[c] = self.selected_membrane.resources.get(c, 0) + 1
        self._actualizar_recursos()
        self.entry_simbolo.delete(0, 'end')

    def _parsear(self, s: str) -> dict:
        ms = {}
        for c in s:
            ms[c] = ms.get(c, 0) + 1
        return ms

    def agregar_regla(self):
        izq = self.entry_izq.get().strip()
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
        if self.var_disolver.get():
            regla.dissolve_membranes.append(self.selected_membrane.id_mem)
        if self.var_crear.get():
            tgt = self.entry_crear.get().strip()
            if tgt not in self.system.skin:
                messagebox.showerror('Error', 'ID destino inválido.')
                return
            regla.create_membranes = [tgt]
        self.selected_membrane.add_regla(regla)
        # Confirmación
        self.lbl_status.config(text=f'Regla añadida correctamente', foreground='green')
        self._actualizar_reglas()
        for e in (self.entry_izq, self.entry_der, self.entry_prioridad):
            e.delete(0, 'end')
        self.entry_prioridad.insert(0, '1')
        self.var_disolver.set(False)
        self.var_crear.set(False)
        self.entry_crear.delete(0, 'end')
        self.entry_crear.configure(state='disabled')

    def on_save(self):
        # Guardar y cerrar
        self.saved = True
        self.destroy()


def configurar_sistema_p():
    app = ConfiguradorPSistema()
    app.mainloop()
    return app.system if app.saved else None

if __name__ == '__main__':
    sistema = configurar_sistema_p()
    print(sistema)
