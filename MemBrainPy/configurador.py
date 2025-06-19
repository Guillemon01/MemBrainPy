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
        self.saved = False
        self.exit_membrane_id = None

        # Cierre
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self._construir_interfaz()

        # Inicializar sistema con membrana raíz
        root = Membrana(id_mem='1', resources={})
        self.mem_counter = 1
        self.system = SistemaP()
        self.system.add_membrane(root, None)
        self.tree.insert('', 'end', '1', text=self._texto_membrana(root))
        self.tree.selection_set('1')
        self.on_select(None)

    def _on_close(self):
        self.saved = False
        self.destroy()

    def _construir_interfaz(self):
        cont = ttk.Frame(self)
        cont.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=2)
        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(0, weight=1)

        # Árbol de membranas y borrar
        tree_frame = ttk.LabelFrame(cont, text='Estructura de Membranas')
        tree_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame)
        self.tree.heading('#0', text='Membranas')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.grid(row=0, column=0, rowspan=3, sticky='nsew', padx=5, pady=5)
        self.var_salida = tk.BooleanVar()
        ttk.Checkbutton(tree_frame, text='Membrana de salida', variable=self.var_salida,
                        command=self._on_toggle_salida).grid(row=1, column=0, sticky='w', padx=5)
        ttk.Button(tree_frame, text='Borrar membrana', command=self.borrar_membrana).grid(row=2, column=0, sticky='w', padx=5, pady=5)

        # Recursos
        res_frame = ttk.LabelFrame(cont, text='Recursos')
        res_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        res_frame.columnconfigure(1, weight=1)
        ttk.Label(res_frame, text='Símbolos (letras):').grid(row=0, column=0, sticky='e', padx=5)
        self.entry_simbolo = ttk.Entry(res_frame)
        self.entry_simbolo.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(res_frame, text='Añadir recurso', command=self.agregar_recurso).grid(row=0, column=2, padx=5)
        self.lista_recursos = tk.Listbox(res_frame, height=5, font=('Consolas', 10), selectmode='single')
        self.lista_recursos.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
        ttk.Button(res_frame, text='Borrar recurso', command=self.borrar_recurso).grid(row=2, column=0, columnspan=3, sticky='ew', padx=5)

        # Definición de reglas
        regla_frame = ttk.LabelFrame(cont, text='Definición de Reglas')
        regla_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        for i in range(4):
            regla_frame.columnconfigure(i, weight=1)

        # Consumir y producir
        ttk.Label(regla_frame, text='Consumir*:').grid(row=0, column=0, sticky='e', padx=5)
        self.entry_izq = ttk.Entry(regla_frame)
        self.entry_izq.grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(regla_frame, text='Producir:').grid(row=1, column=0, sticky='e', padx=5)
        self.entry_der = ttk.Entry(regla_frame)
        self.entry_der.grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Label(regla_frame, text='Destino:').grid(row=1, column=2, sticky='e', padx=5)
        self.entry_destino = ttk.Entry(regla_frame, width=5)
        self.entry_destino.grid(row=1, column=3, sticky='w', padx=5)

        # Prioridad
        ttk.Label(regla_frame, text='Prioridad:').grid(row=2, column=0, sticky='e', padx=5)
        vcmd = (self.register(self._validate_entero), '%P')
        self.entry_prioridad = ttk.Entry(regla_frame, validate='key', validatecommand=vcmd)
        self.entry_prioridad.insert(0, '1')
        self.entry_prioridad.grid(row=2, column=1, sticky='ew', padx=5)

        # Opciones de disolver / crear / dividir
        self.var_disolver = tk.BooleanVar()
        self.var_crear = tk.BooleanVar()
        self.var_dividir = tk.BooleanVar()

        ttk.Checkbutton(regla_frame, text='Disolver membrana', variable=self.var_disolver,
                        command=self._toggle_options).grid(row=3, column=0, sticky='w', padx=5)
        ttk.Checkbutton(regla_frame, text='Crear membrana', variable=self.var_crear,
                        command=self._toggle_options).grid(row=4, column=0, sticky='w', padx=5)
        ttk.Label(regla_frame, text='ID destino:').grid(row=4, column=1, sticky='e', padx=5)
        self.entry_crear = ttk.Entry(regla_frame, width=5, state='disabled')
        self.entry_crear.grid(row=4, column=2, sticky='w', padx=5)

        ttk.Checkbutton(regla_frame, text='Dividir membrana', variable=self.var_dividir,
                        command=self._toggle_options).grid(row=3, column=2, sticky='w', padx=5)
        ttk.Label(regla_frame, text='Multi v:').grid(row=4, column=2, sticky='e', padx=5)
        self.entry_div_v = ttk.Entry(regla_frame, width=15, state='disabled')
        self.entry_div_v.grid(row=4, column=3, sticky='w', padx=5)
        ttk.Label(regla_frame, text='Multi w:').grid(row=5, column=2, sticky='e', padx=5)
        self.entry_div_w = ttk.Entry(regla_frame, width=15, state='disabled')
        self.entry_div_w.grid(row=5, column=3, sticky='w', padx=5)

        # Botón y estado
        ttk.Button(regla_frame, text='Añadir regla', command=self.agregar_regla)\
            .grid(row=6, column=0, columnspan=4, pady=10)
        self.lbl_status = ttk.Label(regla_frame, text='', font=('Arial', 9, 'italic'))
        self.lbl_status.grid(row=7, column=0, columnspan=4)

        # Lista de reglas y borrar
        reglas_frame = ttk.LabelFrame(cont, text='Reglas de la Membrana Seleccionada')
        reglas_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        reglas_frame.columnconfigure(0, weight=1)
        self.lista_reglas = tk.Listbox(reglas_frame, height=6, font=('Consolas',10), selectmode='single')
        self.lista_reglas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        ttk.Button(reglas_frame, text='Borrar regla', command=self.borrar_regla)\
            .grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        # Panel inferior: agregar membrana, generar aleatorio, guardar
        bottom = ttk.Frame(self)
        bottom.pack(side='bottom', fill='x', padx=10, pady=5)
        ttk.Label(bottom, text='ID Padre nueva membrana:').pack(side='left', padx=5)
        self.entry_padre = ttk.Entry(bottom, width=5)
        self.entry_padre.pack(side='left')
        ttk.Button(bottom, text='Agregar membrana', command=self.agregar_membrana).pack(side='left', padx=5)
        ttk.Button(bottom, text='Generar aleatorio', command=self.generar_sistema_aleatorio).pack(side='left', padx=5)
        ttk.Button(bottom, text='Guardar y salir', command=self.on_save).pack(side='right', padx=10)

    def _validate_entero(self, v):
        return v.isdigit() or v == ''

    def _toggle_options(self):
        # Al activar “Crear”, desactivo Disolver y Dividir
        if self.var_crear.get():
            self.var_disolver.set(False)
            self.var_dividir.set(False)
            self.entry_crear.configure(state='normal')
            self.entry_div_v.configure(state='disabled')
            self.entry_div_w.configure(state='disabled')
        # Al activar “Disolver”, desactivo Crear y Dividir
        elif self.var_disolver.get():
            self.var_crear.set(False)
            self.var_dividir.set(False)
            self.entry_crear.configure(state='disabled')
            self.entry_div_v.configure(state='disabled')
            self.entry_div_w.configure(state='disabled')
        # Al activar “Dividir”, desactivo Crear y Disolver
        elif self.var_dividir.get():
            self.var_crear.set(False)
            self.var_disolver.set(False)
            self.entry_crear.configure(state='disabled')
            self.entry_div_v.configure(state='normal')
            self.entry_div_w.configure(state='normal')
        else:
            # Ninguna opción: todo desactivado
            self.entry_crear.configure(state='disabled')
            self.entry_div_v.configure(state='disabled')
            self.entry_div_w.configure(state='disabled')

    def _texto_membrana(self, m: Membrana) -> str:
        parts = [f"{k}:{v}" for k,v in sorted(m.resources.items())]
        base = f"Membrana {m.id_mem} [{','.join(parts)}]"
        if self.exit_membrane_id == m.id_mem:
            base += " (SALIDA)"
        return base

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        mid = sel[0]
        if not self.tree.exists(mid):
            return
        self.selected_membrane = self.system.skin[mid]
        self._actualizar_recursos()
        self._actualizar_reglas()
        self.var_salida.set(self.exit_membrane_id == mid)

    def _on_toggle_salida(self):
        if not self.selected_membrane: return
        prev = self.exit_membrane_id
        if prev and prev in self.system.skin:
            self.tree.item(prev, text=self._texto_membrana(self.system.skin[prev]))
        if self.var_salida.get():
            self.exit_membrane_id = self.selected_membrane.id_mem
        else:
            self.exit_membrane_id = None
        self.system.output_membrane = self.exit_membrane_id
        for mid, mem in self.system.skin.items():
            self.tree.item(mid, text=self._texto_membrana(mem))

    def _actualizar_recursos(self):
        self.lista_recursos.delete(0, 'end')
        for k,v in sorted(self.selected_membrane.resources.items()):
            self.lista_recursos.insert('end', f"{k}: {v}")

    def _actualizar_reglas(self):
        self.lista_reglas.delete(0, 'end')
        for idx, r in enumerate(self.selected_membrane.reglas):
            consumir = ' '.join(f"{s}×{c}" for s,c in r.left.items())
            prod_items = []
            for simb, cnt in r.right.items():
                if '_in_' in simb:
                    base, target = simb.split('_in_')
                    prod_items.append(f"{base}→{target}×{cnt}")
                else:
                    prod_items.append(f"{simb}×{cnt}")
            prod = ' '.join(prod_items)
            tipo = []
            if r.division:
                tipo.append('DIV')
            if r.create_membranes:
                tipo.append('CREA')
            tipo_str = f"[{','.join(tipo)}] " if tipo else ''
            texto = (
                f"{idx+1}. {tipo_str}"
                f"Consumir: {consumir}"
                + (f" | Producir: {prod}" if prod else '')
                + f" | Prioridad: {r.priority}"
            )
            self.lista_reglas.insert('end', texto)

    def agregar_membrana(self):
        pid = self.entry_padre.get().strip()
        if not pid:
            pid = self.selected_membrane.id_mem if self.selected_membrane else None
        self.mem_counter += 1
        nid = str(self.mem_counter)
        nueva = Membrana(id_mem=nid, resources={})
        parent = pid if pid in self.system.skin else None
        self.system.add_membrane(nueva, parent)
        self.tree.insert(parent or '', 'end', nid, text=self._texto_membrana(nueva))
        self.entry_padre.delete(0, 'end')

    def agregar_recurso(self):
        if not self.selected_membrane:
            messagebox.showwarning('Advertencia', 'Seleccione una membrana primero')
            return
        s = self.entry_simbolo.get().strip()
        if not re.fullmatch(r'[A-Za-z]+', s):
            messagebox.showerror('Error', 'Símbolos ASCII sin acentos')
            return
        for c in s:
            self.selected_membrane.resources[c] = self.selected_membrane.resources.get(c,0) + 1
        self._actualizar_recursos()
        self.entry_simbolo.delete(0, 'end')

    def agregar_regla(self):
        if not self.selected_membrane:
            return

        izq = self.entry_izq.get().strip()
        if self.var_disolver.get() and self.selected_membrane.id_mem == '1':
            messagebox.showerror('Error', 'No disolver membrana raíz')
            return
        if not re.fullmatch(r'[A-Za-z]+', izq):
            messagebox.showerror('Error', 'Campo consumir obligatorio')
            return

        der = self.entry_der.get().strip()
        if der and not re.fullmatch(r'[A-Za-z]+', der):
            messagebox.showerror('Error', 'Campo producir inválido')
            return

        destino = self.entry_destino.get().strip()
        if destino and destino not in self.system.skin:
            messagebox.showerror('Error', f"Membrana destino '{destino}' no existe")
            return

        prio = self.entry_prioridad.get().strip()
        if not prio:
            messagebox.showerror('Error', 'Prioridad obligatoria')
            return

        # Construir multiconjunto de producción normal
        right = {}
        if der:
            parsed = self._parsear(der)
            if destino:
                for s, c in parsed.items():
                    right[f"{s}_in_{destino}"] = c
            else:
                right = parsed

        # Configurar creación de membrana
        create_list = []
        if self.var_crear.get():
            target = self.entry_crear.get().strip()
            if not target:
                messagebox.showerror('Error', 'ID destino obligatorio para crear membrana')
                return
            content_ms = self._parsear(der) if der else {}
            create_list = [(target, content_ms)]

        # Configurar división de membrana
        division_tuple = None
        if self.var_dividir.get():
            v_text = self.entry_div_v.get().strip()
            w_text = self.entry_div_w.get().strip()
            if not v_text or not w_text:
                messagebox.showerror('Error', 'Debe proporcionar multiconjuntos v y w')
                return
            v_ms = self._parsear(v_text)
            w_ms = self._parsear(w_text)
            division_tuple = (v_ms, w_ms)

        # Crear y añadir la regla
        regla = Regla(
            left=self._parsear(izq),
            right=right,
            priority=int(prio),
            create_membranes=create_list,
            division=division_tuple
        )
        self.selected_membrane.reglas.append(regla)
        self.lbl_status.config(text='Regla añadida', foreground='green')
        self._actualizar_reglas()

        # Limpiar campos
        self.entry_izq.delete(0, 'end')
        self.entry_der.delete(0, 'end')
        self.entry_destino.delete(0, 'end')
        self.entry_prioridad.delete(0, 'end')
        self.entry_prioridad.insert(0, '1')
        self.var_disolver.set(False)
        self.var_crear.set(False)
        self.var_dividir.set(False)
        self.entry_crear.configure(state='disabled')
        self.entry_div_v.configure(state='disabled')
        self.entry_div_w.configure(state='disabled')

    def generar_sistema_aleatorio(self):
        self.system = SistemaP()
        self.tree.delete(*self.tree.get_children())
        self.mem_counter = 0
        letras = list('abcdefghijk')
        ids = []
        for _ in range(random.randint(2,6)):
            self.mem_counter+=1
            mid=str(self.mem_counter)
            m=Membrana(id_mem=mid,resources={})
            parent= random.choice(ids) if ids else None
            self.system.add_membrane(m,parent)
            self.tree.insert(parent or '', 'end', mid, text=self._texto_membrana(m))
            ids.append(mid)
            for _ in range(random.randint(0,10)):
                c=random.choice(letras)
                m.resources[c]=m.resources.get(c,0)+1
            for __ in range(random.randint(1,5)):
                left={t:random.randint(1,3) for t in random.sample(letras, random.randint(1,min(3,len(letras))))}
                prod_count=random.randint(0,3)
                right={t:random.randint(1,3) for t in random.sample(letras, prod_count)}
                m.reglas.append(Regla(left=left,right=right,priority=random.randint(1,5)))
        self.exit_membrane_id=random.choice(ids)
        self.system.output_membrane=self.exit_membrane_id
        if ids:
            self.tree.selection_set(ids[0]); self.on_select(None)

    def borrar_recurso(self):
        sel=self.lista_recursos.curselection()
        if not sel:
            messagebox.showwarning('Advertencia','Seleccione un recurso')
            return
        simb=self.lista_recursos.get(sel[0]).split(':')[0]
        del self.selected_membrane.resources[simb]
        self._actualizar_recursos()

    def borrar_regla(self):
        sel=self.lista_reglas.curselection()
        if not sel:
            messagebox.showwarning('Advertencia','Seleccione una regla')
            return
        idx=sel[0]
        self.selected_membrane.reglas.pop(idx)
        self._actualizar_reglas()

    def borrar_membrana(self):
        sel=self.tree.selection()
        if not sel:
            messagebox.showwarning('Advertencia','Seleccione una membrana')
            return
        mid=sel[0]
        if mid=='1':
            messagebox.showerror('Error','No borrar membrana raíz')
            return
        to_delete=[mid]
        for m in reversed(to_delete):
            if hasattr(self.system, 'remove_membrane'):
                self.system.remove_membrane(m)
            else:
                del self.system.skin[m]
            self.tree.delete(m)
        for mem in self.system.skin.values():
            mem.children = [c for c in mem.children if c not in to_delete]
        self.tree.selection_set('1'); self.on_select(None)

    def _parsear(self,s:str)->dict:
        d={}
        for c in s:
            d[c]=d.get(c,0)+1
        return d

    def on_save(self):
        self.saved=True
        self.destroy()

def configurar_sistema_p():
    app=ConfiguradorPSistema()
    app.mainloop()
    return app.system if app.saved else None

if __name__=='__main__':
    sistema=configurar_sistema_p()
    print(sistema)
