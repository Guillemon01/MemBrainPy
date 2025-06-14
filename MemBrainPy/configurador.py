import tkinter as tk
from tkinter import ttk, messagebox
import re
from SistemaP import SistemaP, Membrana, Regla

class ConfiguradorPSistema(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configurador de Sistema P")
        self.system = SistemaP()
        self.selected_membrane = None
        self.mem_counter = 1
        self._construir_interfaz()

    def _construir_interfaz(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Árbol de membranas
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='Membranas')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.grid(row=0, column=0, rowspan=8, sticky='nsew', padx=5, pady=5)

        # Panel de creación de membrana genérica
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        btn_agregar_mem = ttk.Button(btn_frame, text='Agregar Membrana', command=self.agregar_membrana)
        btn_agregar_mem.pack(side='left', padx=5)
        ttk.Label(btn_frame, text='Padre ID:').pack(side='left')
        self.entry_padre = ttk.Entry(btn_frame, width=5)
        self.entry_padre.pack(side='left', padx=2)
        btn_crear_padre = ttk.Button(btn_frame, text='Crear en Padre', command=self.crear_en_padre)
        btn_crear_padre.pack(side='left', padx=5)

        # Sección recursos
        res_frame = ttk.LabelFrame(self, text='Agregar Recurso')
        res_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.entry_simbolo = ttk.Entry(res_frame)
        self.entry_simbolo.grid(row=0, column=0, padx=5, pady=5)
        btn_agregar_recurso = ttk.Button(res_frame, text='Agregar a Membrana', command=self.agregar_recurso)
        btn_agregar_recurso.grid(row=0, column=1, padx=5, pady=5)
        self.lista_recursos = tk.Listbox(res_frame, height=4)
        self.lista_recursos.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Sección reglas
        regla_frame = ttk.LabelFrame(self, text='Definir Regla')
        regla_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        ttk.Label(regla_frame, text='Consumir:').grid(row=0, column=0)
        self.entry_izq = ttk.Entry(regla_frame)
        self.entry_izq.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(regla_frame, text='Producir:').grid(row=1, column=0)
        self.entry_der = ttk.Entry(regla_frame)
        self.entry_der.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(regla_frame, text='Prioridad:').grid(row=2, column=0)
        vcmd = (self.register(self._validate_entero), '%P')
        self.entry_prioridad = ttk.Entry(regla_frame, validate='key', validatecommand=vcmd)
        self.entry_prioridad.insert(0, '1')
        self.entry_prioridad.grid(row=2, column=1, padx=5, pady=2)
        # Checkbox disolver y crear membrana
        self.var_disolver = tk.BooleanVar()
        self.var_crear = tk.BooleanVar()
        chk_disolver = ttk.Checkbutton(regla_frame, text='Disuelve membrana', variable=self.var_disolver,
                                       command=self._toggle_options)
        chk_disolver.grid(row=3, column=0, sticky='w', padx=5)
        ttk.Label(regla_frame, text='Crear membrana ID:').grid(row=4, column=0)
        self.entry_crear = ttk.Entry(regla_frame, width=5)
        self.entry_crear.grid(row=4, column=1, sticky='w', padx=5)
        chk_crear = ttk.Checkbutton(regla_frame, text='', variable=self.var_crear, command=self._toggle_options)
        chk_crear.grid(row=4, column=2, sticky='w')
        btn_agregar_regla = ttk.Button(regla_frame, text='Agregar Regla', command=self.agregar_regla)
        btn_agregar_regla.grid(row=5, column=0, columnspan=3, pady=5)
        self.lbl_status = ttk.Label(regla_frame, text='')
        self.lbl_status.grid(row=6, column=0, columnspan=3)

        # Botón guardar
        btn_guardar = ttk.Button(self, text='Guardar y Salir', command=self.on_save)
        btn_guardar.grid(row=7, column=1, sticky='e', padx=5, pady=5)

        # Membrana inicial (piel)
        piel = Membrana(id_mem=str(self.mem_counter), resources={})
        self.system.add_membrane(piel, None)
        self.tree.insert('', 'end', str(self.mem_counter), text=self._texto_membrana(piel))

    def _validate_entero(self, valor):
        return valor.isdigit() or valor == ''

    def _toggle_options(self):
        # Evitar ambas opciones simultáneas
        if self.var_disolver.get():
            self.var_crear.set(False)
            self.entry_crear.configure(state='disabled')
        elif self.var_crear.get():
            self.var_disolver.set(False)
            self.entry_crear.configure(state='normal')
        else:
            self.entry_crear.configure(state='disabled')

    def _texto_membrana(self, membrana: Membrana) -> str:
        if membrana.resources:
            items = sorted(membrana.resources.items())
            res_str = ','.join(f'{k}:{v}' for k, v in items)
            return f'Membrana {membrana.id_mem} [{res_str}]'
        return f'Membrana {membrana.id_mem} []'

    def on_select(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            mem_id = seleccion[0]
            self.selected_membrane = self.system.skin[mem_id]
            self._actualizar_recursos()

    def _actualizar_recursos(self):
        self.lista_recursos.delete(0, tk.END)
        for sim, cnt in sorted(self.selected_membrane.resources.items()):
            self.lista_recursos.insert(tk.END, f"{sim}: {cnt}")
        self.tree.item(self.selected_membrane.id_mem,
                       text=self._texto_membrana(self.selected_membrane))

    def agregar_membrana(self):
        self.mem_counter += 1
        nuevo_id = str(self.mem_counter)
        nueva = Membrana(id_mem=nuevo_id, resources={})
        seleccion = self.tree.selection()
        if seleccion:
            padre_id = seleccion[0]
            self.system.add_membrane(nueva, padre_id)
            self.tree.insert(padre_id, 'end', nuevo_id, text=self._texto_membrana(nueva))
        else:
            raices = self.tree.get_children('')
            self.system.add_membrane(nueva, None)
            self.tree.insert('', 'end', nuevo_id, text=self._texto_membrana(nueva))
            for rid in raices:
                mem = self.system.skin[rid]
                mem.parent = nuevo_id
                self.system.skin[nuevo_id].children.append(rid)
                self.tree.move(rid, nuevo_id, 'end')

    def crear_en_padre(self):
        pid = self.entry_padre.get().strip()
        if pid not in self.system.skin:
            messagebox.showerror('Error', f"Membrana padre '{pid}' no existe.")
            return
        self.mem_counter += 1
        nuevo_id = str(self.mem_counter)
        nueva = Membrana(id_mem=nuevo_id, resources={})
        self.system.add_membrane(nueva, pid)
        self.tree.insert(pid, 'end', nuevo_id, text=self._texto_membrana(nueva))
        self.entry_padre.delete(0, tk.END)

    def agregar_recurso(self):
        sim = self.entry_simbolo.get().strip()
        if not re.fullmatch(r'[A-Za-z]+', sim):
            messagebox.showerror('Error', 'El símbolo debe contener solo letras ASCII sin acentos.')
            return
        if self.selected_membrane:
            rec = self.selected_membrane.resources
            for c in sim:
                rec[c] = rec.get(c, 0) + 1
            self._actualizar_recursos()
            self.entry_simbolo.delete(0, tk.END)

    def _parsear_multiconjunto(self, cadena: str) -> dict:
        ms = {}
        for c in cadena.strip():
            ms[c] = ms.get(c, 0) + 1
        return ms

    def agregar_regla(self):
        self.lbl_status.config(text='', foreground='')
        izq = self.entry_izq.get().strip()
        if not re.fullmatch(r'[A-Za-z]+', izq):
            messagebox.showerror('Error', 'La cadena consumir es obligatoria y debe contener solo letras ASCII sin acentos.')
            return
        der = self.entry_der.get().strip()
        if der and not re.fullmatch(r'[A-Za-z]+', der):
            messagebox.showerror('Error', 'La cadena producir debe contener solo letras ASCII sin acentos o estar vacía.')
            return
        prio = self.entry_prioridad.get().strip()
        if prio == '':
            messagebox.showerror('Error', 'La prioridad es obligatoria.')
            return
        prioridad = int(prio)
        left_ms = self._parsear_multiconjunto(izq)
        right_ms = self._parsear_multiconjunto(der) if der else {}
        regla = Regla(left=left_ms, right=right_ms, priority=prioridad)
        # Disolver membrana
        if self.var_disolver.get() and self.selected_membrane:
            regla.dissolve_membranes.append(self.selected_membrane.id_mem)
        # Crear membrana
        if self.var_crear.get():
            target_id = self.entry_crear.get().strip()
            if not target_id or target_id not in self.system.skin:
                messagebox.showerror('Error', 'ID destino para crear membrana inválido.')
                return
            regla.create_membranes = [target_id]
        if self.selected_membrane:
            self.selected_membrane.add_regla(regla)
            self.lbl_status.config(text=f'Regla añadida (prio {prioridad})', foreground='green')
            # Reset campos
            self.entry_izq.delete(0, tk.END)
            self.entry_der.delete(0, tk.END)
            self.entry_prioridad.delete(0, tk.END)
            self.entry_prioridad.insert(0, '1')
            self.var_disolver.set(False)
            self.var_crear.set(False)
            self.entry_crear.delete(0, tk.END)
            self.entry_crear.configure(state='disabled')

    def on_save(self):
        self.destroy()


def configurar_sistema_p():
    app = ConfiguradorPSistema()
    app.mainloop()
    return app.system

if __name__ == '__main__':
    sistema = configurar_sistema_p()
    print(sistema)
