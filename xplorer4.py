#!/usr/bin/python3.9
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk, filedialog
import os
import shutil
import subprocess
from collections import OrderedDict
import time
import stat
import base64

class ExploradorNV(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Archivos de Novatitrox")
        self.geometry("1100x650")
        
        # Variables
        self.current_path = "/mnt"
        self.allowed_path = "/mnt"
        self.selected_item = ""
        self.search_term = tk.StringVar()
        self.search_results = []
        self.clipboard = {"action": None, "path": None}  # Para copiar/mover
        self.file_associations = {}  # Para asociaciones de archivos
        
        # Cargar íconos
        self.load_icons()
        
        # Cargar asociaciones de archivos
        self.load_file_associations()
        
        # Interfaz
        self.create_widgets()
        self.update_file_list()
    
    def load_file_associations(self):
        """Carga las asociaciones de archivos desde el archivo de configuración"""
        associations_file = "/mnt/sda1/home/sistema/files.txt"
        try:
            if os.path.exists(associations_file):
                with open(associations_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split("=")
                            if len(parts) == 2:
                                ext = parts[0].strip().lower()
                                program = parts[1].strip()
                                self.file_associations[ext] = program
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar asociaciones de archivos: {str(e)}")
    
    def load_icons(self):
        """Carga íconos usando imágenes base64 integradas"""
        try:
            # Ícono de carpeta en formato XBM (compatible nativo con Tkinter)
            folder_icon_data = """
            #define folder_width 16
            #define folder_height 16
            static unsigned char folder_bits[] = {
               0x00, 0x00, 0xfe, 0x3f, 0x03, 0x60, 0xfd, 0x5f, 0x05, 0x50, 0x05, 0x50,
               0x05, 0x50, 0x05, 0x50, 0x05, 0x50, 0x05, 0x50, 0x05, 0x50, 0x05, 0x50,
               0x05, 0x50, 0xfd, 0x5f, 0x03, 0x60, 0xfe, 0x3f
            };
            """
            self.folder_icon = tk.BitmapImage(data=folder_icon_data, foreground='blue')
            
            # Ícono de archivo genérico (XBM)
            file_icon_data = """
            #define file_width 16
            #define file_height 16
            static unsigned char file_bits[] = {
               0xff, 0xff, 0x01, 0x80, 0x7d, 0xbe, 0x45, 0xa2, 0x45, 0xa2, 0x45, 0xa2,
               0x45, 0xa2, 0x45, 0xa2, 0x45, 0xa2, 0x45, 0xa2, 0x45, 0xa2, 0x45, 0xa2,
               0x45, 0xa2, 0x7d, 0xbe, 0x01, 0x80, 0xff, 0xff
            };
            """
            self.file_icon = tk.BitmapImage(data=file_icon_data, foreground='black')
            
            # Ícono de disco/partición (XBM)
            drive_icon_data = """
            #define drive_width 16
            #define drive_height 16
            static unsigned char drive_bits[] = {
               0x00, 0x00, 0xf0, 0x0f, 0x0c, 0x30, 0x02, 0x40, 0x01, 0x80, 0xf1, 0x8f,
               0x11, 0x88, 0x11, 0x88, 0x11, 0x88, 0x11, 0x88, 0xf1, 0x8f, 0x01, 0x80,
               0x02, 0x40, 0x0c, 0x30, 0xf0, 0x0f, 0x00, 0x00
            };
            """
            self.drive_icon = tk.BitmapImage(data=drive_icon_data, foreground='orange')
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar íconos: {str(e)}")
            # Íconos por defecto simples si hay error
            self.folder_icon = tk.PhotoImage(width=16, height=16)
            self.folder_icon.put("blue", to=(0, 0, 15, 15))
            self.file_icon = tk.PhotoImage(width=16, height=16)
            self.file_icon.put("black", to=(0, 0, 15, 15))
            self.drive_icon = tk.PhotoImage(width=16, height=16)
            self.drive_icon.put("orange", to=(0, 0, 15, 15))

def create_widgets(self):
    # Fondo general
    self.configure(bg="#f0f0f0")

    # Frame de búsqueda
    search_frame = tk.Frame(self, bg="#e6e6e6", bd=2, relief="groove")
    search_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(search_frame, text="Buscar:", bg="#e6e6e6", font=("Arial", 10, "bold")).pack(side="left", padx=(5, 0))
    tk.Entry(search_frame, textvariable=self.search_term, width=40, font=("Arial", 10)).pack(side="left", padx=5)
    tk.Button(search_frame, text="Buscar", command=self.search_files, bg="#4caf50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    tk.Button(search_frame, text="Limpiar", command=self.clear_search, bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

    # Barra superior
    top_frame = tk.Frame(self, bg="#e6e6e6", bd=2, relief="groove")
    top_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(top_frame, text="Ruta:", bg="#e6e6e6", font=("Arial", 10, "bold")).pack(side="left", padx=(5, 0))
    self.path_label = tk.Label(top_frame, text="/mnt", relief="sunken", width=70, anchor="w", bg="white", font=("Arial", 10))
    self.path_label.pack(side="left", padx=5)
    tk.Button(top_frame, text="Volver", command=self.go_back, bg="#607d8b", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

    # Frame para el Treeview y scrollbars
    list_frame = tk.Frame(self, bg="#f0f0f0")
    list_frame.pack(expand=True, fill="both", padx=5, pady=5)

    # Treeview para mostrar archivos en columnas
    self.tree = ttk.Treeview(list_frame, columns=("Nombre", "Tipo", "Tamaño", "Modificado"), selectmode="browse", show="headings")
    self.tree.heading("Nombre", text="Nombre", anchor="w")
    self.tree.heading("Tipo", text="Tipo", anchor="w")
    self.tree.heading("Tamaño", text="Tamaño", anchor="w")
    self.tree.heading("Modificado", text="Modificado", anchor="w")

    # Configurar columnas
    self.tree.column("Nombre", width=300, minwidth=150, anchor="w")
    self.tree.column("Tipo", width=150, minwidth=100, anchor="w")
    self.tree.column("Tamaño", width=100, minwidth=80, anchor="w")
    self.tree.column("Modificado", width=150, minwidth=100, anchor="w")

    # Scrollbars
    yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
    xscroll = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
    self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    # Grid layout
    self.tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")

    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    # Botones
    btn_frame = tk.Frame(self, bg="#f0f0f0")
    btn_frame.pack(fill="x", padx=5, pady=5)

    button_style = {"bg": "#008cba", "fg": "white", "font": ("Arial", 10, "bold"), "padx": 5, "pady": 2}
    tk.Button(btn_frame, text="Abrir", command=self.open_item, **button_style).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Renombrar", command=self.rename_item, **button_style).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Crear Carpeta", command=self.create_folder, **button_style).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Eliminar", command=self.delete_item, bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Copiar", command=self.copy_item, **button_style).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Mover", command=self.move_item, **button_style).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Pegar", command=self.paste_item, bg="#4caf50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=2)

    # Eventos
    self.tree.bind("<Double-Button-1>", lambda e: self.open_item())
    self.tree.bind("<Return>", lambda e: self.open_item())

    # Menú contextual
    self.menu = tk.Menu(self, tearoff=0, bg="#ffffff", fg="#000000", font=("Arial", 10))
    self.menu.add_command(label="Abrir", command=self.open_item)
    self.menu.add_command(label="Renombrar", command=self.rename_item)
    self.menu.add_command(label="Eliminar", command=self.delete_item)
    self.menu.add_separator()
    self.menu.add_command(label="Copiar", command=self.copy_item)
    self.menu.add_command(label="Mover", command=self.move_item)
    self.menu.add_command(label="Pegar", command=self.paste_item)
    self.menu.add_separator()
    self.menu.add_command(label="Crear Carpeta", command=self.create_folder)
    self.menu.add_separator()
    self.menu.add_command(label="Copiar Ruta", command=self.copy_path)

    self.tree.bind("<Button-3>", self.show_context_menu)
    
    def create_folder(self):
        """Crea una nueva carpeta en el directorio actual"""
        # Ventana de diálogo para nombre de carpeta
        self.new_folder_window = tk.Toplevel(self)
        self.new_folder_window.title("Crear Carpeta")
        self.new_folder_window.geometry("400x150")
        
        tk.Label(self.new_folder_window, text="Nombre de la nueva carpeta:").pack(pady=10)
        
        self.new_folder_var = tk.StringVar()
        tk.Entry(self.new_folder_window, textvariable=self.new_folder_var, width=40).pack(pady=5)
        
        tk.Button(self.new_folder_window, text="Crear", command=self.do_create_folder).pack(side="left", padx=20)
        tk.Button(self.new_folder_window, text="Cancelar", command=self.new_folder_window.destroy).pack(side="right", padx=20)
    
    def do_create_folder(self):
        """Ejecuta la creación de la carpeta"""
        folder_name = self.new_folder_var.get().strip()
        if not folder_name:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        new_path = os.path.join(self.current_path, folder_name)
        
        try:
            os.mkdir(new_path)
            messagebox.showinfo("Éxito", f"Carpeta '{folder_name}' creada correctamente")
            self.new_folder_window.destroy()
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta:\n{str(e)}")
    
    def show_context_menu(self, event):
        """Muestra menú contextual al hacer clic derecho"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
    
    def get_selected_path(self):
        """Obtiene la ruta completa del elemento seleccionado"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        selected = self.tree.item(selection[0])['values'][0]
        
        # Si es una partición montada (formato especial)
        if self.current_path == "/mnt" and "(" in selected and ")" in selected:
            selected = selected.split("(")[1].split(")")[0]
        
        return os.path.join(self.current_path, selected)
    
    def rename_item(self):
        """Inicia el proceso de renombrado"""
        old_path = self.get_selected_path()
        if not old_path:
            messagebox.showerror("Error", "Selecciona un archivo o carpeta primero")
            return
        
        # Ventana de diálogo para nuevo nombre
        self.rename_window = tk.Toplevel(self)
        self.rename_window.title("Renombrar")
        self.rename_window.geometry("400x150")
        
        tk.Label(self.rename_window, text=f"Renombrar:\n{os.path.basename(old_path)}").pack(pady=10)
        
        self.new_name_var = tk.StringVar(value=os.path.basename(old_path))
        tk.Entry(self.rename_window, textvariable=self.new_name_var, width=40).pack(pady=5)
        
        tk.Button(self.rename_window, text="Aceptar", command=lambda: self.do_rename(old_path)).pack(side="left", padx=20)
        tk.Button(self.rename_window, text="Cancelar", command=self.rename_window.destroy).pack(side="right", padx=20)
    
    def do_rename(self, old_path):
        """Ejecuta el renombrado"""
        new_name = self.new_name_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        
        try:
            os.rename(old_path, new_path)
            messagebox.showinfo("Éxito", "Elemento renombrado correctamente")
            self.rename_window.destroy()
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo renombrar:\n{str(e)}")
    
    def delete_item(self):
        """Elimina el archivo o carpeta seleccionado"""
        path = self.get_selected_path()
        if not path:
            messagebox.showerror("Error", "Selecciona un archivo o carpeta primero")
            return
        
        # Confirmación antes de eliminar
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar '{os.path.basename(path)}'?")
        if not confirm:
            return
        
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)  # Elimina directorio y todo su contenido
            else:
                os.remove(path)  # Elimina archivo
            
            messagebox.showinfo("Éxito", "Elemento eliminado correctamente")
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")
    
    def copy_item(self):
        """Copia el archivo/carpeta al portapapeles para pegarlo después"""
        path = self.get_selected_path()
        if path:
            self.clipboard = {"action": "copy", "path": path}
            messagebox.showinfo("Copiado", f"Elemento copiado:\n{path}")
    
    def move_item(self):
        """Mueve el archivo/carpeta al portapapeles para pegarlo después"""
        path = self.get_selected_path()
        if path:
            self.clipboard = {"action": "move", "path": path}
            messagebox.showinfo("Movido", f"Elemento listo para mover:\n{path}")
    
    def paste_item(self):
        """Pega el elemento copiado/movido en el directorio actual"""
        if not self.clipboard["path"]:
            messagebox.showerror("Error", "No hay nada para pegar")
            return
        
        source = self.clipboard["path"]
        action = self.clipboard["action"]
        dest = os.path.join(self.current_path, os.path.basename(source))
        
        # Si el destino ya existe
        if os.path.exists(dest):
            confirm = messagebox.askyesno("Confirmar", f"'{os.path.basename(dest)}' ya existe. ¿Sobrescribir?")
            if not confirm:
                return
        
        try:
            if action == "copy":
                if os.path.isdir(source):
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
                messagebox.showinfo("Éxito", "Elemento copiado correctamente")
            elif action == "move":
                shutil.move(source, dest)
                messagebox.showinfo("Éxito", "Elemento movido correctamente")
            
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo {action}:\n{str(e)}")
    
    def copy_path(self):
        """Copia la ruta al portapapeles"""
        path = self.get_selected_path()
        if path:
            self.clipboard_clear()
            self.clipboard_append(path)
            messagebox.showinfo("Copiado", f"Ruta copiada:\n{path}")
    
    def get_partition_info(self):
        """Obtiene nombres reales de particiones usando blkid"""
        partitions = {}
        try:
            blkid_output = subprocess.check_output(["sudo", "blkid"]).decode("utf-8")
            for line in blkid_output.splitlines():
                if "/dev/" in line:
                    dev = line.split(":")[0]
                    label = None
                    if "LABEL=" in line:
                        label = line.split('LABEL="')[1].split('"')[0]
                    partitions[os.path.basename(dev)] = label
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer particiones: {str(e)}")
        return partitions

    def get_file_size(self, path):
        """Obtiene el tamaño del archivo formateado"""
        try:
            size = os.path.getsize(path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024*1024:
                return f"{size/1024:.1f} KB"
            elif size < 1024*1024*1024:
                return f"{size/(1024*1024):.1f} MB"
            else:
                return f"{size/(1024*1024*1024):.1f} GB"
        except:
            return "N/A"

    def get_modified_time(self, path):
        """Obtiene la fecha de modificación formateada"""
        try:
            mtime = os.path.getmtime(path)
            return time.strftime("%d/%m/%Y %H:%M", time.localtime(mtime))
        except:
            return "N/A"

    def search_files(self):
        """Busca archivos por nombre en /mnt"""
        term = self.search_term.get().lower()
        if not term:
            messagebox.showwarning("Error", "Ingresa un término de búsqueda")
            return
        
        self.search_results = []
        self.tree.delete(*self.tree.get_children())
        
        try:
            for root, dirs, files in os.walk("/mnt"):
                for file in files:
                    if term in file.lower():
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, "/mnt")
                        self.search_results.append(full_path)
                        
                        # Obtener información del archivo
                        file_type = "Archivo"
                        size = self.get_file_size(full_path)
                        modified = self.get_modified_time(full_path)
                        
                        self.tree.insert("", "end", text="", image=self.file_icon, values=(rel_path, file_type, size, modified))
            
            if not self.search_results:
                messagebox.showinfo("Info", "No se encontraron resultados")
            else:
                self.path_label.config(text=f"Resultados: {len(self.search_results)} archivos")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo en búsqueda:\n{str(e)}")

    def clear_search(self):
        """Vuelve a mostrar el directorio actual"""
        self.search_term.set("")
        self.search_results = []
        self.update_file_list()
    
    def update_file_list(self):
        """Actualiza la lista mostrando archivos y carpetas con íconos"""
        self.tree.delete(*self.tree.get_children())
        
        if self.search_results:  # No actualizar si hay búsqueda activa
            return
           
        self.path_label.config(text=f"Ruta: {self.current_path}")
        
        try:
            if self.current_path == "/mnt":
                partition_info = self.get_partition_info()
                for entry in sorted(os.listdir(self.current_path)):
                    full_path = os.path.join(self.current_path, entry)
                    if os.path.islink(full_path):
                        continue
                    
                    if os.path.ismount(full_path):
                        # Mostrar nombre de partición o dispositivo si no tiene nombre
                        label = partition_info.get(entry, f"Dispositivo {entry}")
                        display = f"{label} ({entry})" if label else entry
                        self.tree.insert("", "end", text="", image=self.drive_icon, 
                                       values=(display, "Partición", "-", "-"))
                    elif os.path.isdir(full_path):
                        modified = self.get_modified_time(full_path)
                        self.tree.insert("", "end", text="", image=self.folder_icon, 
                                       values=(entry, "Carpeta", "-", modified))
            else:
                # Mostrar contenido del directorio actual
                for entry in sorted(os.listdir(self.current_path)):
                    full_path = os.path.join(self.current_path, entry)
                    
                    if os.path.isdir(full_path):
                        # Carpeta con ícono personalizado
                        modified = self.get_modified_time(full_path)
                        self.tree.insert("", "end", text="", image=self.folder_icon, 
                                       values=(entry, "Carpeta", "-", modified))
                    else:
                        # Archivo con ícono genérico
                        file_type = "Archivo"
                        if "." in entry:
                            ext = entry.split(".")[-1].upper()
                            file_type = f"Archivo {ext}"
                        
                        size = self.get_file_size(full_path)
                        modified = self.get_modified_time(full_path)
                        self.tree.insert("", "end", text="", image=self.file_icon, 
                                       values=(entry, file_type, size, modified))
            
            self.path_label.config(text=f"Ruta actual: {self.current_path}")
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo acceder: {str(e)}")
            self.go_back()
    
    def open_item(self, event=None):
        """Abre la partición/carpeta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Si hay resultados de búsqueda
        if self.search_results:
            full_path = self.search_results[int(selection[0][1:])-1]  # Obtener índice del item
            if os.path.isdir(full_path):
                self.current_path = full_path
                self.clear_search()
            else:
                self.open_with_program(full_path)
            return
        
        # Resto de la lógica para navegación normal
        selected = self.tree.item(selection[0])['values'][0]
        
        # Extraer nombre real si es una partición
        if self.current_path == "/mnt" and "(" in selected and ")" in selected:
            selected = selected.split("(")[1].split(")")[0]
        
        new_path = os.path.join(self.current_path, selected)
        
        # Validar ruta permitida
        if not new_path.startswith(self.allowed_path):
            messagebox.showerror("Error", "Acceso restringido fuera de /mnt")
            return
        
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.update_file_list()
        else:
            self.open_with_program(new_path)
    
    def open_with_program(self, file_path):
        """Abre el archivo con el programa asociado a su extensión"""
        # Obtener extensión del archivo
        ext = os.path.splitext(file_path)[1].lower()
        if ext.startswith('.'):
            ext = ext[1:]  # Quitar el punto
            
        # Buscar programa asociado
        program = self.file_associations.get(ext)
        
        try:
            if program:
                # Usar el programa específico si está definido
                subprocess.Popen([program, file_path])
            else:
                # Usar xdg-open como fallback
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")
    
    def go_back(self):
        """Retrocede un nivel"""
        if self.current_path == self.allowed_path:
            return
        self.current_path = os.path.dirname(self.current_path)
        self.update_file_list()

if __name__ == "__main__":
    app = ExploradorNV()
    app.mainloop()
