import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import sqlite3, datetime, os, time, shutil, ctypes, sys
from tkinter.scrolledtext import ScrolledText

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ManageRB")
        def get_icon_path():
            if getattr(sys, 'frozen', False):
                return os.path.join(sys._MEIPASS, "ico.ico")
            else:
                return "ico.ico"

        icon_path = get_icon_path()

        root.iconbitmap(icon_path)
        
        root.state('zoomed')
        root.resizable(True, False)
        
        root.minsize(width=1000, height=300)
        
        # Request for Administrator privileges
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

        if not is_admin():
            root = tk.Tk()
            root.withdraw()

            messagebox.showwarning("Warning", "This program only works with Administrator privileges.")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

        # Database connection
        self.connection = None
        self.sort_column = None
        
        # Creating files
        logs_directory = os.path.join("C:\\", "Windows", "ManageRB")
        logs_file_path = os.path.join(logs_directory, "LOGS.txt")

        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory)

        self.log_file_path = logs_file_path

        # Main menu
        self.menu_frame = ttk.Frame(root, padding="10")
        self.menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.menu_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        button_styles = {
            "font": ("Comic Sans MS", 10),
        }

        button_colors = {
            "Create.TButton": "green",
            "Choose.TButton": "dark violet",
            "Edit.TButton": "blue",
            "Delete.TButton": "red",
            "Show.TButton": "purple",
            "Discount.TButton": "brown",
            "Total.TButton": "purple",
            "SuperDiscount.TButton": "brown",
            "Log.TButton": "dark violet",
        }

        # Main options buttons
        ttk.Button(self.menu_frame, text="Create database", command=self.create_database, takefocus=False, style="Create.TButton").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Choose database", command=self.choose_database, takefocus=False, style="Choose.TButton").grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Logs", command=self.open_logs_window, takefocus=False, style="Log.TButton").grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Edit row", command=self.edit_row, takefocus=False, style="Edit.TButton").grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Delete row", command=self.delete_row, takefocus=False, style="Delete.TButton").grid(row=0, column=4, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Calculate discount", command=self.calculate_discount, takefocus=False, style="Discount.TButton").grid(row=0, column=5, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Super Discount", command=self.super_discount, takefocus=False, style="SuperDiscount.TButton").grid(row=0, column=6, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Calculate total quantity", command=self.calculate_total_quantity, takefocus=False, style="Total.TButton").grid(row=0, column=7, padx=5, pady=5, sticky="nsew")
        ttk.Button(self.menu_frame, text="Show entire database", command=self.show_entire_database, takefocus=False, style="Show.TButton").grid(row=0, column=8, padx=5, pady=5, sticky="nsew")

        self.menu_frame.style = ttk.Style()
        for style_name, color in button_colors.items():
            self.menu_frame.style.configure(style_name, foreground=color, **button_styles)

        # Treeview for displaying product table
        self.tree_frame = ttk.Frame(root, padding="10")
        self.tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)

        root.update_idletasks()
        window_height = root.winfo_height()
        tree_height = int(0.023 * window_height)

        columns = ("ID", "Name", "Code", "Price", "Color", "Sizes", "Quantity")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=tree_height)

        style = ttk.Style()
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        font=('Comic Sans MS', 10)
                        )
        style.map("Treeview", background=[('selected', '#347083')])

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tree(c))
            self.tree.column(col, anchor='center')

            style.configure("Treeview.Heading", font=('Comic Sans MS', 12))

        self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Entry fields for data input
        self.entry_frame = ttk.Frame(root, padding="10")
        self.entry_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.entry_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        labels = ("Name", "Code", "Price", "Color", "Sizes", "Quantity")
        self.label_variables = []

        for i, col in enumerate(columns[1:]):
            label = ttk.Label(self.entry_frame, text=labels[i], font=("Comic Sans MS", 10))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            var = tk.StringVar()
            entry = ttk.Entry(self.entry_frame, textvariable=var)
            entry.grid(row=1, column=i, padx=5, pady=5, sticky="nsew")
            self.label_variables.append(var)

        ttk.Button(self.entry_frame, text="Add item", command=self.add_product_entry, takefocus=False, style="Create.TButton").grid(row=1, column=len(columns), padx=5, pady=5, sticky="nsew")

        self.editing_id = None

        # Search fields
        self.search_frame = ttk.Frame(root, padding="10")
        self.search_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.search_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        search_labels = ("Name", "Code", "Price", "Color", "Sizes", "Quantity")
        self.search_variables = []

        for i, col in enumerate(search_labels):
            label = ttk.Label(self.search_frame, text=col, font=("Comic Sans MS", 10))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            var = tk.StringVar()
            entry = ttk.Entry(self.search_frame, textvariable=var)
            entry.grid(row=1, column=i, padx=5, pady=5, sticky="nsew")
            self.search_variables.append(var)

        ttk.Button(self.search_frame, text="Search", command=self.search_products, takefocus=False, style="Edit.TButton").grid(row=1, column=len(search_labels), padx=5, pady=5, sticky="nsew")

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0, font=("Comic Sans MS", 10))
        self.context_menu.configure(fg="dark violet", bg="light gray")

        self.context_menu.add_command(label="Edit row", command=self.edit_row, font=("Comic Sans MS", 10), foreground="blue", background="light gray")
        self.context_menu.add_command(label="Copy row", command=self.copy_row, font=("Comic Sans MS", 10), foreground="dark violet", background="light gray")
        self.context_menu.add_command(label="Paste row", command=self.paste_row, font=("Comic Sans MS", 10), foreground="dark violet", background="light gray")
        self.context_menu.add_command(label="Delete row", command=self.delete_row, font=("Comic Sans MS", 10), foreground="red", background="light gray")

        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.selected_row = None
        self.dragged_row = None
        self.new_row_index = None
        self.tree.bind("<Button-1>", self.on_click)
        self.tree.bind("<B1-Motion>", self.on_drag)
        self.tree.bind("<ButtonRelease-1>", self.on_release)
    
    # Database check
    def audit_bd (self):
        if not self.connection:
            messagebox.showerror("Error", "No database selected.")
            return

    # Show context menu
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        self.tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)
        
    # Copy
    def copy_row(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.copied_row = self.tree.item(selected_item, 'values')
            messagebox.showinfo("Success", "Row copied.")
        else:
            messagebox.showinfo("Attention", "Select a row to copy.")
            
    # Paste
    def paste_row(self):
        if not hasattr(self, 'copied_row') or not self.copied_row:
            messagebox.showinfo("Увага", "Немає рядка для вставки.")
            return

        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM products ORDER BY id ASC")
        existing_ids = set(row[0] for row in cursor.fetchall())

        # Знаходження найменшого доступного ID
        next_id = 1
        while next_id in existing_ids:
            next_id += 1

        new_values = [next_id] + list(self.copied_row[1:])

        cursor.execute('''
            INSERT INTO products (id, name, code, price, color, sizes, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', new_values)

        self.connection.commit()

        self.tree.insert('', 'end', values=new_values)
        self.display_products()
        messagebox.showinfo("Success", "Row inserted.")
        
    # Right-click
    def on_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.selected_row = row_id
            
    # Drag right-click
    def on_drag(self, event):
        if self.selected_row:
            new_row_id = self.tree.identify_row(event.y)
            if new_row_id and new_row_id != self.selected_row:
                self.dragged_row = self.selected_row
                self.new_row_index = self.tree.index(new_row_id)
                self.tree.move(self.dragged_row, '', self.new_row_index)
                
    # Release right-click
    def on_release(self, event):
        if self.selected_row:
            self.selected_row = None
            self.dragged_row = None
            self.new_row_index = None
            self.update_data()
            
    # Data update
    def update_data(self):
        cursor = self.connection.cursor()
        for i, item in enumerate(self.tree.get_children()):
            new_values = list(self.tree.item(item, 'values'))
            new_values[0] = i + 1  # Оновлюємо ID
            # Оновлюємо інші дані
            cursor.execute("UPDATE products SET Name=?, Code=?, Price=?, Color=?, Sizes=?, Quantity=? WHERE id=?",
                           (new_values[1], new_values[2], new_values[3], new_values[4], new_values[5], new_values[6], new_values[0]))
            self.tree.item(item, values=new_values)
        self.connection.commit()
        cursor.close()
        
    # Create database
    def create_database(self):
        create_db_window = tk.Toplevel(self.root)
        create_db_window.title("Database Creation")
    
        window_width = 300
        window_height = 120

        screen_width = create_db_window.winfo_screenwidth()
        screen_height = create_db_window.winfo_screenheight()

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        create_db_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        label = ttk.Label(create_db_window, text="Enter the name of the database:")
        label.pack(pady=10)

        entry_var = tk.StringVar()
        entry = ttk.Entry(create_db_window, textvariable=entry_var)
        entry.pack(pady=5)

        def create_database_action():
            database_name = entry_var.get()
            if database_name:
                self.connection = sqlite3.connect(f'{database_name}.db')
                self.create_table()
                create_db_window.destroy()

                # Створення файлу журналу
                logs_directory = os.path.join("C:\\", "Windows", "ManageRB", database_name)
                logs_file_path = os.path.join(logs_directory, "LOGS.txt")

                if not os.path.exists(logs_directory):
                    os.makedirs(logs_directory)

                # Збереження шляху до файлу журналу
                self.log_file_path = logs_file_path

                messagebox.showinfo("Information", f"The database named '{database_name}' has been successfully created.")

        create_button = ttk.Button(create_db_window, text="Create", command=create_database_action, takefocus=False)
        create_button.pack(pady=10)
        
    # Logs
    def open_logs_window(self):
        if not self.connection:
            messagebox.showerror("Error", "No database selected.")
            return
        
        if not hasattr(self, 'logs_window') or not self.logs_window.winfo_exists():
            self.logs_window = tk.Toplevel(self.root)
            self.logs_window.title("Logs")
            self.logs_window.minsize(width=400, height=350)
        
            window_width = 600
            window_height = 500

            screen_width = self.logs_window.winfo_screenwidth()
            screen_height = self.logs_window.winfo_screenheight()

            x_position = (screen_width - window_width) // 2
            y_position = (screen_height - window_height) // 2

            self.logs_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            logs_textbox = ScrolledText(self.logs_window, wrap=tk.WORD, width=60, height=20, font=("Arial", 12))
            logs_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            with open(self.log_file_path, "r") as logs_file:
                logs_content = logs_file.read()
                logs_textbox.insert(tk.END, logs_content)

                tag_starts = {
                    "[CHANGED]": "blue",
                    "[DELETED]": "red",
                    "[SUPER DISCOUNT]": "green"
                }

                for tag, color in tag_starts.items():
                    start_index = "1.0"
                    while True:
                        start_index = logs_textbox.search(tag, start_index, tk.END)
                        if not start_index:
                            break
                        end_index = f"{start_index}+{len(tag)}c"
                        logs_textbox.tag_add(tag, start_index, end_index)
                        logs_textbox.tag_config(tag, foreground=color)
                        start_index = end_index
                        start_index = logs_textbox.search("\n", start_index, tk.END)

            logs_textbox.config(state=tk.DISABLED)

            ttk.Style().configure("Exit.TButton", foreground="red", font=("Arial", 10))

            ttk.Button(self.logs_window, text="Exit", command=self.logs_window.destroy, style="Exit.TButton", takefocus=False).grid(row=1, column=0, pady=10)

            self.logs_window.columnconfigure(0, weight=1)
            self.logs_window.rowconfigure(0, weight=1)
        
            logs_textbox.see(tk.END)
        else:
            self.logs_window.lift()
        
    # Show entire database
    def show_entire_database(self):
        self.audit_bd()

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())

        for product in products:
            self.tree.insert("", "end", values=product)
            
    # Calculate total quantity
    def calculate_total_quantity(self):
        self.audit_bd()

        cursor = self.connection.cursor()
        cursor.execute("SELECT SUM(quantity) FROM products")
        total_quantity = cursor.fetchone()[0]

        messagebox.showinfo("Total Quantity", f"Total quantity in the database: {total_quantity}")
        
    # Super discount
    def super_discount(self):
        if not self.connection:
            messagebox.showerror("Error", "No database selected.")
            return

        if hasattr(self, 'super_discount_window') and self.super_discount_window.winfo_exists():
            self.super_discount_window.lift()
            return

        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Attention", "Select rows for calculating the super discount.")
            return

        self.super_discount_window = tk.Toplevel(self.root)
        self.super_discount_window.title("Super Discount")

        window_width = 250
        window_height = 180

        screen_width = self.super_discount_window.winfo_screenwidth()
        screen_height = self.super_discount_window.winfo_screenheight()

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.super_discount_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.super_discount_window.configure(bg="light gray")

        self.super_discount_window.resizable(False, False)

        font = ("Comic Sans MS", 12)
        font_title = ("Comic Sans MS", 16, "underline")

        style = ttk.Style()
        style.configure("Custom.TLabel", font=font, foreground="dark violet", background="light gray")
        style.configure("Custom.TButton", font=font, foreground="dark violet", background="light gray")
        style.configure("Custom.TCheckbutton", font=font, foreground="dark violet", background="light gray")

        title_label = ttk.Label(self.super_discount_window, text="Super Discount", style="Custom.TLabel", font=font_title)
        title_label.pack(pady=10)

        discount_var = tk.StringVar()

        discount_entry_frame = ttk.Frame(self.super_discount_window)
        discount_entry_frame.pack(pady=5)

        def validate_discount_input(char, entry_value):
            return char.isdigit() or (char == "" and entry_value and entry_value[:-1].isdigit()) or (char == "-" and not entry_value)

        validate_discount = discount_entry_frame.register(validate_discount_input)
        discount_entry = ttk.Entry(discount_entry_frame, textvariable=discount_var, font=font, justify="center", width=10, validate="key", validatecommand=(validate_discount, "%S", "%P"))
        discount_entry.grid(row=0, column=0)

        percent_label = ttk.Label(discount_entry_frame, text="%", style="Custom.TLabel")
        percent_label.grid(row=0, column=1, sticky="nsew")

        def on_entry_click(event):
            if discount_var.get() == "0":
                discount_entry.delete(0, "end")
                discount_entry.insert(0, "")

        def on_focus_out(event):
            if not discount_var.get():
                discount_var.set("0")

        discount_entry.insert(0, "0")
        discount_entry.bind("<FocusIn>", on_entry_click)
        discount_entry.bind("<FocusOut>", on_focus_out)

        def apply_super_discount():
            try:
                discount_percentage = float(discount_var.get())
                if neg_var.get():
                    discount_percentage *= -1
            except ValueError:
                messagebox.showerror("Error", "Invalid value for super discount.")
                self.super_discount_window.focus_force()
                return

            if not -100 <= discount_percentage <= 100:
                messagebox.showinfo("Attention", "Enter a valid percentage for the super discount (-100 to 100).")
                self.super_discount_window.focus_force()
                return

            selected_ids = [(item_values[0], item_values[1], item_values[3]) for item in selected_items for item_values in [self.tree.item(item, 'values')]]
            self.write_to_logs("SUPER DISCOUNT", selected_ids, additional_info=f"{discount_percentage}%")

            for item in selected_items:
                item_values = self.tree.item(item, 'values')
                if len(item_values) >= 4:
                    try:
                        current_price = float(item_values[3])
                        discounted_price = round(current_price * (1 - discount_percentage / 100))

                        # Оновити дані в базі даних
                        cursor = self.connection.cursor()
                        cursor.execute("UPDATE products SET price=? WHERE id=?", (discounted_price, item_values[0]))
                        self.connection.commit()

                        # Оновити дані в таблиці
                        self.tree.item(item, values=(item_values[0], item_values[1], item_values[2], discounted_price, item_values[4], item_values[5], item_values[6]))
                    except (ValueError, IndexError):
                        messagebox.showerror("Error", "Invalid data for calculating the super discount.")
                        self.super_discount_window.focus_force()

            self.super_discount_window.destroy()
        
        neg_var = tk.BooleanVar()
        neg_checkbox = ttk.Checkbutton(self.super_discount_window, text="Increase price", variable=neg_var, style="Custom.TCheckbutton", takefocus=False)
        neg_checkbox.pack(pady=5)

        apply_button = ttk.Button(self.super_discount_window, text="Apply Super Discount", command=apply_super_discount, style="Custom.TButton", takefocus=False)
        apply_button.pack(pady=5)
        
    # Calculate discount
    def calculate_discount(self):
        if not self.connection:
            messagebox.showerror("Error", "No database selected.")
            return
        
        if hasattr(self, 'discount_window') and self.discount_window.winfo_exists():
            self.discount_window.lift()
            return
            
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Attention", "Select a row to calculate the discount.")
            return
    
        selected_items = self.tree.selection()
        if not selected_items or len(selected_items) != 1:
            messagebox.showinfo("Attention", "Select one row to calculate the discount.")
            return

        try:
            initial_price = float(self.tree.item(selected_item, 'values')[3])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid data for calculating the discount.")
            return

        self.discount_window = tk.Toplevel(self.root)
        self.discount_window.title("Calculate Discount")

        window_width = 330
        window_height = 300

        screen_width = self.discount_window.winfo_screenwidth()
        screen_height = self.discount_window.winfo_screenheight()

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.discount_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.discount_window.configure(bg="light gray")

        self.discount_window.resizable(False, False)

        font = ("Comic Sans MS", 12)
        font_title = ("Comic Sans MS", 16, "underline")

        style = ttk.Style()
        style.configure("Custom.TLabel", font=font, foreground="dark violet", background="light gray")
        style.configure("Custom.TButton", font=font, foreground="dark violet", background="light gray")
        style.configure("Custom.TCheckbutton", font=font, foreground="dark violet", background="light gray")

        title_label = ttk.Label(self.discount_window, text="Calculate Discount", style="Custom.TLabel", font=font_title)
        title_label.pack(pady=10)

        discount_var = tk.StringVar()

        entry_label = ttk.Label(self.discount_window, text="Initial price:", style="Custom.TLabel")
        entry_label.pack(pady=5)

        price_label = ttk.Label(self.discount_window, text=f"{initial_price}$", style="Custom.TLabel")
        price_label.pack(pady=5)

        discount_entry_frame = ttk.Frame(self.discount_window)
        discount_entry_frame.pack(pady=5)

        def validate_discount_input(char, entry_value):
            return char.isdigit() or (char == "" and entry_value and entry_value[:-1].isdigit())

        validate_discount = discount_entry_frame.register(validate_discount_input)
        discount_entry = ttk.Entry(discount_entry_frame, textvariable=discount_var, font=font, justify="center", width=10, validate="key", validatecommand=(validate_discount, "%S", "%P"))
        discount_entry.grid(row=0, column=0)

        percent_label = ttk.Label(discount_entry_frame, text="%", style="Custom.TLabel")
        percent_label.grid(row=0, column=1, sticky="nsew")

        def on_entry_click(event):
            if discount_var.get() == "0":
                discount_entry.delete(0, "end")
                discount_entry.insert(0, "")

        def on_focus_out(event):
            if not discount_var.get():
                discount_var.set("0")

        discount_entry.insert(0, "0")
        discount_entry.bind("<FocusIn>", on_entry_click)
        discount_entry.bind("<FocusOut>", on_focus_out)

        def calculate_discount_action():
            discount_value = discount_var.get()

            if not discount_value:
                messagebox.showerror("Error", "Enter the discount value.")
                self.discount_window.focus_force()
                return
            try:
                discount_percentage = int(discount_value)
                if not -100 <= discount_percentage <= 100:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid discount value. Enter a number from -100 to 100.")
                self.discount_window.focus_force()
                return

            if neg_var.get():
                discount_percentage *= -1

            discounted_price = initial_price * (100 - discount_percentage) // 100 
            result_label.config(text=f"Price with discount: {discounted_price}$")

        neg_var = tk.BooleanVar()
        neg_checkbox = ttk.Checkbutton(self.discount_window, text="Increase price", variable=neg_var, style="Custom.TCheckbutton", takefocus=False)
        neg_checkbox.pack(pady=5)

        calculate_button = ttk.Button(self.discount_window, text="Calculate Discount", command=calculate_discount_action, style="Custom.TButton", takefocus=False)
        calculate_button.pack(pady=5)

        result_label = ttk.Label(self.discount_window, text="", style="Custom.TLabel")
        result_label.pack(pady=5)
        
    # Create table
    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                code TEXT,
                price REAL,
                color TEXT,
                sizes TEXT,
                quantity INTEGER
            )
        ''')
        self.connection.commit()
    
    # Choose database and create backup    
    def choose_database(self):
        database_name = filedialog.askopenfilename(filetypes=[("SQLite databases", "*.db")])
        if database_name:
            self.connection = sqlite3.connect(database_name)

            logs_directory = os.path.join("C:\\", "Windows", "ManageRB", os.path.splitext(os.path.basename(database_name))[0])
            self.log_file_path = os.path.join(logs_directory, "LOGS.txt")

            if not os.path.exists(logs_directory):
                os.makedirs(logs_directory)

            if not os.path.exists(self.log_file_path):
                with open(self.log_file_path, "w"):
                    pass

            # Резервна копія бази даних
            backup_path = os.path.join(logs_directory, os.path.basename(database_name))
            if os.path.exists(backup_path):
                # Оновлення резервної копії бази даних
                shutil.copyfile(database_name, backup_path)
            else:
                shutil.copyfile(database_name, backup_path)

            self.display_products()
            
    # Add item
    def add_product_entry(self):
        self.audit_bd()

        # Перевірка чи всі поля для введення є порожніми
        if all(var.get() == '' for var in self.label_variables):
            messagebox.showerror("Error", "Enter data to add a new item.")
            return

        data = tuple(var.get() for var in self.label_variables)
        if data:
            if self.editing_id is not None:
                # Ви редагуєте існуючий рядок
                cursor = self.connection.cursor()
                cursor.execute('''
                    SELECT * FROM products
                    WHERE id=?
                ''', (self.editing_id,))
                existing_row = cursor.fetchone()

                self.write_to_logs("CHANGED", [self.editing_id], existing_row, data)

                # Оновлення існуючого рядка
                cursor.execute('''
                    UPDATE products
                    SET name=?, code=?, price=?, color=?, sizes=?, quantity=?
                    WHERE id=?
                ''', data + (self.editing_id,))
            else:
                cursor = self.connection.cursor()
                cursor.execute("SELECT id FROM products ORDER BY id ASC")
                existing_ids = set(row[0] for row in cursor.fetchall())

                # Знаходження найменшого доступного ID
                next_id = 1
                while next_id in existing_ids:
                    next_id += 1

                # Вставка нового товару з наступним доступним ID
                cursor.execute('''
                    INSERT INTO products (id, name, code, price, color, sizes, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (next_id,) + data)

            self.connection.commit()
            self.display_products()
            for var in self.label_variables:
                var.set('')
                
    # Write to logs
    def write_to_logs(self, action, selected_rows, old_data=None, new_data=None, additional_info=None):
        current_datetime = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")

        log_entry = f"\n[{action.upper()}] - {current_datetime}\n"

        if action.upper() == 'SUPER DISCOUNT':
            log_entry += f"({additional_info})\n"
            for row_id, name, price in selected_rows:
                log_entry += f"{row_id}| {name}| Price before discount: {price}\n"
        else:
            log_entry += f"{selected_rows[0]}\n"
            if old_data is not None:
                log_entry += ' | '.join(map(str, old_data[1:])) + "\n"
            if new_data is not None:
                log_entry += ' | '.join(map(str, new_data)) + "\n"
    
        with open(self.log_file_path, "a") as log_file:
            log_file.write(log_entry)
            
    # Show items
    def display_products(self):
        self.audit_bd()

        cursor = self.connection.cursor()
    
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            messagebox.showerror("Error", "The 'products' table is missing in the selected database.")
            return

        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())

        for product in products:
            self.tree.insert("", "end", values=product)
            
    # Find item
    def search_products(self):
        self.audit_bd()

        search_criteria = []
        for label, var in zip(("name", "code", "price", "color", "sizes", "quantity"), self.search_variables):
            value = var.get()
            if value:
                search_criteria.append(f"{label} LIKE ?")

        if not search_criteria:
            messagebox.showinfo("Search", "No search criteria.")
            return

        search_query = " AND ".join(search_criteria)

        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM products WHERE {search_query}', tuple(f"%{var.get()}%" for var in self.search_variables if var.get()))
        products = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())

        for product in products:
            self.tree.insert("", "end", values=product)
            
    # Edit row
    def edit_row(self):
        selected_items = self.tree.selection()
        if not selected_items or len(selected_items) != 1:
            messagebox.showinfo("Attention", "Select one row to edit.")
            return

        selected_values = self.tree.item(selected_items[0], 'values')
        selected_id = selected_values[0]
        selected_values = selected_values[1:]

        for var, value in zip(self.label_variables, selected_values):
            var.set(value)

        self.editing_id = selected_id
        
    # Delete row
    def delete_row(self):
        selected_items = self.tree.selection()
        if not selected_items or len(selected_items) != 1:
            messagebox.showinfo("Attention", "Select one row to delete.")
            return

        selected_id = self.tree.item(selected_items[0], 'values')[0]

        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM products
            WHERE id=?
        ''', (selected_id,))
        deleted_row_data = cursor.fetchone()

        confirmation = messagebox.askquestion("Deletion Confirmation", "Are you sure you want to delete the selected row?", icon="warning")

        if confirmation == "yes":
            self.write_to_logs("DELETED", [selected_id], deleted_row_data)

            cursor.execute("DELETE FROM products WHERE id=?", (selected_id,))
            self.connection.commit()

            cursor.execute("SELECT id FROM products ORDER BY id")
            row_ids = [row[0] for row in cursor.fetchall()]

            for index, row_id in enumerate(row_ids, start=1):
                cursor.execute("UPDATE products SET id=? WHERE id=?", (index, row_id))
        
            self.connection.commit()

            self.display_products()
            
    # Sort row
    def sort_tree(self, column):
        self.audit_bd()

        cursor = self.connection.cursor()

        if self.sort_column == column:
            self.sort_order = not self.sort_order
        else:
            self.sort_order = True
            self.sort_column = column

        order = "ASC" if self.sort_order else "DESC"
        cursor.execute(f'SELECT * FROM products ORDER BY {column} {order}')
        products = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())

        for product in products:
            self.tree.insert("", "end", values=product)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.columnconfigure(0, weight=1)
    root.rowconfigure((0, 1, 2, 3), weight=1)
    root.mainloop()
