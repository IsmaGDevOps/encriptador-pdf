import os
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import Levenshtein  # Asegúrate de instalar esta librería con `pip install python-Levenshtein`

def open_csv_editor(csv_file_var):
    """Abre un editor para visualizar, modificar y completar el archivo CSV en un cuadro de diálogo."""
    csv_file = csv_file_var.get()
    if not csv_file:
        messagebox.showerror("Error", "Por favor, selecciona un archivo CSV primero.")
        return

    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo CSV: {e}")
        return

    # Crear un cuadro de diálogo para el editor
    editor_window = tk.Toplevel()
    editor_window.title("Editor de CSV")
    editor_window.geometry("600x450")
    editor_window.resizable(False, False)

    # Frame para la tabla
    table_frame = ttk.Frame(editor_window)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Crear la tabla
    tree = ttk.Treeview(table_frame, columns=(1, 2), show='headings', height=15, selectmode="browse")
    tree.pack(fill=tk.BOTH, expand=True)

    # Configurar encabezados
    tree.heading(1, text="Nombre del PDF")
    tree.heading(2, text="Contraseña")
    tree.column(1, width=300)
    tree.column(2, width=200)

    # Rellenar la tabla con los datos del CSV
    for row in rows:
        if len(row) >= 2:
            tree.insert("", tk.END, values=(row[0], row[1]))
        else:
            tree.insert("", tk.END, values=(row[0], ""))

    # Habilitar edición de celdas
    def on_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            open_row_editor(is_new=False, item=selected_item[0])

    tree.bind("<Double-1>", on_double_click)

    # Funciones para añadir y eliminar filas
    def add_row():
        open_row_editor(is_new=True)

    def delete_row():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una fila para eliminar.")
            return
        for item in selected_item:
            tree.delete(item)

    # Función para guardar los cambios
    def save_changes():
        try:
            new_rows = [tree.item(row)["values"] for row in tree.get_children()]
            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(new_rows)
            messagebox.showinfo("Éxito", "Los cambios se han guardado correctamente.")
            editor_window.destroy()  # Cerrar el editor después de guardar
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo CSV: {e}")

    # Botones de control
    button_frame = ttk.Frame(editor_window)
    button_frame.pack(fill=tk.X, pady=10)

    # Usar grid para distribuir uniformemente los botones
    save_button = ttk.Button(button_frame, text="Guardar Cambios", command=save_changes)
    save_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    add_button = ttk.Button(button_frame, text="Añadir Fila", command=add_row)
    add_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    delete_button = ttk.Button(button_frame, text="Eliminar Fila", command=delete_row)
    delete_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    close_button = ttk.Button(button_frame, text="Cerrar", command=editor_window.destroy)
    close_button.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

    # Ajustar las columnas para distribuir el espacio uniformemente
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)

    def open_row_editor(is_new, item=None):
        """Abre un cuadro de diálogo para añadir o editar una fila."""
        editor = tk.Toplevel(editor_window)
        editor.title("Editar Fila" if not is_new else "Añadir Fila")
        editor.geometry("400x200")
        editor.resizable(False, False)

        # Variables de entrada
        pdf_name_var = tk.StringVar(value="" if is_new else tree.item(item, "values")[0])
        password_var = tk.StringVar(value="" if is_new else tree.item(item, "values")[1])

        # Etiquetas y entradas
        tk.Label(editor, text="Nombre del PDF:").pack(pady=5)
        pdf_name_entry = ttk.Entry(editor, textvariable=pdf_name_var)
        pdf_name_entry.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(editor, text="Contraseña:").pack(pady=5)
        password_entry = ttk.Entry(editor, textvariable=password_var)
        password_entry.pack(fill=tk.X, padx=10, pady=5)

        # Función para guardar cambios
        def save_row():
            pdf_name = pdf_name_var.get().strip()
            password = password_var.get().strip()

            if not pdf_name:
                messagebox.showerror("Error", "El nombre del PDF no puede estar vacío.")
                return

            if is_new:
                tree.insert("", tk.END, values=(pdf_name, password))
            else:
                tree.item(item, values=(pdf_name, password))

            editor.destroy()

        # Botones
        save_button = ttk.Button(editor, text="Guardar", command=save_row)
        save_button.pack(side=tk.RIGHT, padx=10, pady=10)

        cancel_button = ttk.Button(editor, text="Cancelar", command=editor.destroy)
        cancel_button.pack(side=tk.RIGHT, pady=10)


def load_passwords_from_csv(csv_file):
    """Carga las contraseñas desde un archivo CSV."""
    passwords = {}
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    pdf_name, password = row[0], row[1]
                    passwords[pdf_name] = password
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {e}")
    return passwords

def verify_passwords(input_folder, passwords):
    """Verifica si todos los archivos PDF tienen contraseñas asignadas."""
    missing_passwords = []
    for file in os.listdir(input_folder):
        if file.endswith('.pdf') and not find_closest_match(file, passwords):
            missing_passwords.append(file)
    return missing_passwords

def find_closest_match(file_name, passwords, threshold=0.7):
    """Encuentra el nombre más similar al archivo en la lista de contraseñas."""
    best_match = None
    best_similarity = 0

    for pdf_name in passwords.keys():
        similarity = Levenshtein.ratio(file_name.lower(), pdf_name.lower())
        if similarity > best_similarity and similarity >= threshold:
            best_match = pdf_name
            best_similarity = similarity

    return best_match

def encrypt_pdfs(input_folder, output_folder, passwords, progress_callback=None):
    """Encripta los PDFs usando las contraseñas proporcionadas."""
    total_files = len([f for f in os.listdir(input_folder) if f.endswith('.pdf')])
    processed_files = 0
    results = []  # Para guardar los resultados de encriptación

    for file in os.listdir(input_folder):
        if file.endswith('.pdf'):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)

            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Buscar coincidencia aproximada para el nombre del archivo
            closest_match = find_closest_match(file, passwords)
            if closest_match:
                writer.encrypt(passwords[closest_match])
                results.append((file, passwords[closest_match]))  # Registrar el archivo y la contraseña usada
            else:
                # Si no se encuentra coincidencia, ignorar el archivo
                print(f"No se encontró contraseña para el archivo: {file}")
                continue

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            processed_files += 1
            if progress_callback:
                progress_callback(processed_files / total_files)

    return results  # Devolver los resultados


def select_folder(prompt):
    """Abre un diálogo para seleccionar una carpeta."""
    folder = filedialog.askdirectory(title=prompt)
    return folder

def select_csv_file():
    """Abre un diálogo para seleccionar un archivo CSV."""
    file = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")], title="Seleccionar archivo CSV")
    return file

def main():
    root = tk.Tk()
    root.title("Encriptador de PDFs")
    root.geometry("600x500")
    root.resizable(True, True)

    # Estilo ttk
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Arial', 12))
    style.configure('TButton', font=('Arial', 12), padding=6)
    style.configure('TFrame', padding=10)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_label = ttk.Label(main_frame, text="Proceso de encriptación de PDFs", font=("Arial", 16, "bold"))
    title_label.pack(pady=(20, 10))

    # Variables
    input_folder_var = tk.StringVar()
    output_folder_var = tk.StringVar()
    csv_file_var = tk.StringVar()

    def create_folder_selector(label_text, variable):
        frame = ttk.Frame(main_frame)
        frame.pack(fill=tk.X, pady=(5, 0))
        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)
        entry = ttk.Entry(frame, textvariable=variable, state="readonly", width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        button = ttk.Button(frame, text="Seleccionar", command=lambda: variable.set(select_folder(label_text)))
        button.pack(side=tk.LEFT)
        return frame

    create_folder_selector("Carpeta de entrada:", input_folder_var)
    create_folder_selector("Carpeta de salida:", output_folder_var)

    csv_frame = ttk.Frame(main_frame)
    csv_frame.pack(fill=tk.X, pady=(5, 10))
    csv_label = ttk.Label(csv_frame, text="Archivo CSV:")
    csv_label.pack(side=tk.LEFT)
    csv_entry = ttk.Entry(csv_frame, textvariable=csv_file_var, state="readonly", width=40)
    csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    csv_button = ttk.Button(csv_frame, text="Seleccionar", command=lambda: csv_file_var.set(select_csv_file()))
    csv_button.pack(side=tk.LEFT)

    progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress_bar.pack(pady=(10, 20))

    def on_start_click():
        input_folder = input_folder_var.get()
        output_folder = output_folder_var.get()
        csv_file = csv_file_var.get()

        if not all([input_folder, output_folder, csv_file]):
            messagebox.showerror("Error", "Por favor, selecciona las carpetas y el archivo CSV.")
            return

        try:
            passwords = load_passwords_from_csv(csv_file)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")
            return

        if not passwords:
            messagebox.showerror("Error", "El archivo CSV no contiene contraseñas válidas.")
            return

        missing_passwords = verify_passwords(input_folder, passwords)
        if missing_passwords:
            messagebox.showwarning(
                "Advertencia",
                f"Faltan contraseñas para los siguientes archivos:\n{', '.join(missing_passwords)}"
            )

        progress_bar.config(value=0)
        progress_bar.update()

        try:
            results = encrypt_pdfs(
                input_folder, output_folder, passwords,
                progress_callback=lambda progress: progress_bar.config(value=progress * 100)
            )

            # Mostrar los resultados
            if results:
                result_message = "Ficheros encriptados:\n" + "\n".join(
                    [f"{file}: {password}" for file, password in results])
                result_message += f"\n\nTotal: {len(results)} ficheros encriptados."
                messagebox.showinfo("Resultados", result_message)
            else:
                messagebox.showinfo("Resultados", "No se encriptó ningún fichero.")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante la encriptación: {e}")
        finally:
            progress_bar.config(value=0)

    start_button = ttk.Button(main_frame, text="Iniciar Encriptación", command=on_start_click)
    start_button.pack(pady=(10, 20))

    copyright_label = ttk.Label(main_frame, text="Programa desarrollado por Ismael Gómez Calzado ©", font=("Arial", 10, "italic"), foreground="gray", borderwidth=2, relief="solid")
    copyright_label.pack(pady=(0, 10), ipadx=5, ipady=5)

    csv_editor_button = ttk.Button(csv_frame, text="Editar CSV", command=lambda: open_csv_editor(csv_file_var))
    csv_editor_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
