import tkinter as tk
from tkinter import ttk, messagebox
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
        # Configuración de columnas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Vista de árbol de membranas
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='Membranas')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.grid(row=0, column=0, rowspan=5, sticky='nsew', padx=5, pady=5)

        # Botón para agregar membrana
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        btn_agregar_mem = ttk.Button(btn_frame, text='Agregar Membrana', command=self.agregar_membrana)
        btn_agregar_mem.pack(side='left', padx=5)

        # Sección de recursos
        res_frame = ttk.LabelFrame(self, text='Agregar Recurso')
        res_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.entry_simbolo = ttk.Entry(res_frame)
        self.entry_simbolo.grid(row=0, column=0, padx=5, pady=5)
        btn_agregar_recurso = ttk.Button(res_frame, text='Agregar a Membrana', command=self.agregar_recurso)
        btn_agregar_recurso.grid(row=0, column=1, padx=5, pady=5)
        self.lista_recursos = tk.Listbox(res_frame, height=4)
        self.lista_recursos.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Sección de reglas
        regla_frame = ttk.LabelFrame(self, text='Definir Regla')
        regla_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        ttk.Label(regla_frame, text='Consumir:').grid(row=0, column=0)
        self.entry_izq = ttk.Entry(regla_frame)
        self.entry_izq.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(regla_frame, text='Producir:').grid(row=1, column=0)
        self.entry_der = ttk.Entry(regla_frame)
        self.entry_der.grid(row=1, column=1, padx=5, pady=2)
        btn_agregar_regla = ttk.Button(regla_frame, text='Agregar Regla', command=self.agregar_regla)
        btn_agregar_regla.grid(row=2, column=0, columnspan=2, pady=5)

        # Botón guardar
        btn_guardar = ttk.Button(self, text='Guardar y Salir', command=self.on_save)
        btn_guardar.grid(row=4, column=1, sticky='e', padx=5, pady=5)

        # Membrana inicial (piel)
        piel = Membrana(id_mem=str(self.mem_counter), resources={})
        self.system.add_membrane(piel, None)
        self.tree.insert('', 'end', str(self.mem_counter), text=f'Membrana {self.mem_counter}')

    def on_select(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            mem_id = seleccion[0]
            self.selected_membrane = self.system.skin[mem_id]
            self._actualizar_recursos()

    def _actualizar_recursos(self):
        self.lista_recursos.delete(0, tk.END)
        for sim, cnt in self.selected_membrane.resources.items():
            self.lista_recursos.insert(tk.END, f"{sim}: {cnt}")

    def agregar_membrana(self):
        # Crear nueva membrana con ID
        self.mem_counter += 1
        nuevo_id = str(self.mem_counter)
        nueva = Membrana(id_mem=nuevo_id, resources={})

        seleccion = self.tree.selection()
        if seleccion:
            # Si hay membrana seleccionada, agregar como hija
            padre_id = seleccion[0]
            self.system.add_membrane(nueva, padre_id)
            self.tree.insert(padre_id, 'end', nuevo_id, text=f'Membrana {nuevo_id}')
        else:
            # Si no hay selección, engloba a todas las raíces
            # Obtener raíces actuales
            raices = self.tree.get_children('')
            self.system.add_membrane(nueva, None)
            self.tree.insert('', 'end', nuevo_id, text=f'Membrana {nuevo_id}')
            for rid in raices:
                # Reasignar en sistema
                mem = self.system.skin[rid]
                mem.parent = nuevo_id
                self.system.skin[nuevo_id].children.append(rid)
                # Mover en treeview
                self.tree.move(rid, nuevo_id, 'end')

    def agregar_recurso(self):
        sim = self.entry_simbolo.get().strip()
        if self.selected_membrane and sim:
            rec = self.selected_membrane.resources
            rec[sim] = rec.get(sim, 0) + 1
            self._actualizar_recursos()
            self.entry_simbolo.delete(0, tk.END)

    def _parsear_multiconjunto(self, cadena):
        ms = {}
        for c in cadena.strip():
            ms[c] = ms.get(c, 0) + 1
        return ms

    def agregar_regla(self):
        izq = self._parsear_multiconjunto(self.entry_izq.get())
        der = self._parsear_multiconjunto(self.entry_der.get())
        regla = Regla(left=izq, right=der, priority=1)
        if self.selected_membrane:
            self.selected_membrane.add_regla(regla)
            messagebox.showinfo('Regla Agregada', repr(regla))
            self.entry_izq.delete(0, tk.END)
            self.entry_der.delete(0, tk.END)

    def on_save(self):
        self.destroy()


def configurar_sistema_p():
    app = ConfiguradorPSistema()
    app.mainloop()
    return app.system

if __name__ == '__main__':
    sistema = configurar_sistema_p()
    print(sistema)
