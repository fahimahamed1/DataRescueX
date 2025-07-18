import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import psutil
from PIL import Image, ImageTk

class RecoveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DataRescueX")
        self.root.geometry("1280x800")
        self.is_dark_mode = False

        # Variables
        self.selected_drive = tk.StringVar()
        self.selected_category = tk.StringVar(value="[All Files]")
        self.recover_mode = tk.StringVar(value="Just Recover")
        self.deep_scan = tk.BooleanVar()
        self.full_scan = tk.BooleanVar()
        self.find_lost = tk.BooleanVar()
        self.scan_custom_list = tk.BooleanVar()
        self.show_preview_var = tk.BooleanVar(value=True)
        self.select_all_var = tk.BooleanVar()
        self.tree_view_var = tk.BooleanVar()
        self.total_files_found = tk.StringVar(value="Total Files: 0")
        self.search_text = tk.StringVar()

        self.files = []
        self.stop_scan = False
        self.scan_thread = None
        self.scan_progress = tk.DoubleVar(value=0.0)

        self.custom_extensions = [".mp4", ".mkv", ".avi"]
        self.style_ui()
        self.build_gui()

    def style_ui(self):
        self.style = ttk.Style()
        self.apply_light_theme()

    def apply_light_theme(self):
        s = self.style
        s.theme_use("clam")
        s.configure("Treeview", background="#ffffff", foreground="#333333", rowheight=28, fieldbackground="#ffffff")
        s.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#4d93c6", foreground="white")
        s.configure("TButton", font=("Segoe UI", 10), padding=6, background="#4d93c6", foreground="white")
        s.map("TButton", background=[("active", "#5ba8d6")])
        s.configure("TLabel", background="#f0f8ff", font=("Segoe UI", 10), foreground="#333333")
        s.configure("TCheckbutton", background="#f0f8ff", font=("Segoe UI", 10), foreground="#333333")
        s.configure("TCombobox", font=("Segoe UI", 10))
        s.configure("TProgressbar", thickness=20, background="#4d93c6", troughcolor="#d6e9f7")
        self.root.configure(bg="#f0f8ff")

    def apply_dark_theme(self):
        s = self.style
        s.theme_use("clam")
        s.configure("Treeview", background="#2e2e2e", foreground="#dcdcdc", rowheight=28, fieldbackground="#2e2e2e")
        s.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#555555", foreground="white")
        s.configure("TButton", font=("Segoe UI", 10), padding=6, background="#555555", foreground="white")
        s.map("TButton", background=[("active", "#777777")])
        s.configure("TLabel", background="#1e1e1e", font=("Segoe UI", 10), foreground="#dcdcdc")
        s.configure("TCheckbutton", background="#1e1e1e", font=("Segoe UI", 10), foreground="#dcdcdc")
        s.configure("TCombobox", font=("Segoe UI", 10))
        s.configure("TProgressbar", thickness=20, background="#555555", troughcolor="#444444")
        self.root.configure(bg="#1e1e1e")

    def build_gui(self):
        self.build_drive_table()
        self.build_controls()
        self.build_content_area()
        self.build_footer()
        self.build_status_bar()

    def build_drive_table(self):
        columns = ("Drive", "File System", "Total Space", "Free Space")
        self.drive_table = ttk.Treeview(self.root, columns=columns, show="headings", height=4)
        for col in columns:
            self.drive_table.heading(col, text=col)
            self.drive_table.column(col, anchor="center")
        self.drive_table.pack(fill="x", padx=10, pady=(8, 0))
        self.populate_drive_info()

    def populate_drive_info(self):
        self.drive_table.delete(*self.drive_table.get_children())
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total = f"{usage.total / (1024 ** 3):.2f} GB"
                free = f"{usage.free / (1024 ** 3):.2f} GB"
                self.drive_table.insert("", "end", values=(part.device, part.fstype, total, free))
            except:
                self.drive_table.insert("", "end", values=(part.device, part.fstype, "-", "-"))

    def build_controls(self):
        control_frame = tk.Frame(self.root, bg=self.root["bg"])
        control_frame.pack(fill="x", padx=10, pady=8)

        ttk.Button(control_frame, text="Scan", command=self.start_scan).grid(row=0, column=0, padx=5)
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.cancel_scan, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Recover", command=self.recover_files).grid(row=0, column=2, padx=5)

        ttk.Label(control_frame, text="Category:").grid(row=0, column=3, padx=5)
        category_menu = ttk.Combobox(control_frame, textvariable=self.selected_category, state="readonly", width=18)
        category_menu['values'] = ["[Pictures]", "[Music]", "[Documents]", "[Videos]", "[Compressed]", "[All Files]"]
        category_menu.grid(row=0, column=4, padx=5)

        search_frame = tk.Frame(control_frame, bg=self.root["bg"])
        search_frame.grid(row=0, column=5, padx=5)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_text, width=25)
        search_entry.pack(side="left")
        self.search_text.trace_add("write", self.filter_file_table)

        scan_opt_frame = tk.Frame(control_frame, bg=self.root["bg"])
        scan_opt_frame.grid(row=0, column=6, padx=10)
        ttk.Checkbutton(scan_opt_frame, text="Deep Scan", variable=self.deep_scan).grid(row=0, column=0)
        ttk.Checkbutton(scan_opt_frame, text="Full Scan", variable=self.full_scan).grid(row=0, column=1)
        ttk.Checkbutton(scan_opt_frame, text="Find Lost Files", variable=self.find_lost).grid(row=0, column=2)
        ttk.Checkbutton(scan_opt_frame, text="Scan Custom List", variable=self.scan_custom_list).grid(row=0, column=3)
        ttk.Button(scan_opt_frame, text="Edit", command=self.edit_custom_extensions).grid(row=0, column=4)

        self.progress_bar = ttk.Progressbar(self.root, variable=self.scan_progress, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)

    def build_content_area(self):
        content_frame = tk.Frame(self.root, bg=self.root["bg"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(content_frame, bg=self.root["bg"])
        left_frame.pack(side="left", fill="both", expand=True)

        self.file_table = ttk.Treeview(left_frame,
                                       columns=("File Name", "File Path", "File Size", "Condition"),
                                       show="headings", selectmode="extended")
        for col in ("File Name", "File Path", "File Size", "Condition"):
            self.file_table.heading(col, text=col)
            self.file_table.column(col, anchor="w", width=150 if col == "File Name" else 300)
        self.file_table.pack(fill="both", expand=True)
        self.file_table.bind("<<TreeviewSelect>>", self.on_file_select)

        preview_frame = tk.Frame(content_frame, bg="#ffffff", width=250, bd=1, relief="solid")
        preview_frame.pack(side="right", fill="y")

        tk.Label(preview_frame, text="Preview", bg="#4d93c6", fg="white",
                 font=("Segoe UI", 11, "bold")).pack(fill="x")
        self.preview_label = tk.Label(preview_frame, text="No Preview Available",
                                      bg="#ffffff", wraplength=220, justify="left")
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)

    def build_footer(self):
        footer = tk.Frame(self.root, bg="#dceffd", bd=1, relief="ridge")
        footer.pack(fill="x", padx=10, pady=(3, 0))
        ttk.Checkbutton(footer, text="Tree View", variable=self.tree_view_var).pack(side="left", padx=5)
        ttk.Checkbutton(footer, text="Select All", variable=self.select_all_var, command=self.toggle_select_all).pack(side="left", padx=5)
        ttk.Checkbutton(footer, text="Show Preview", variable=self.show_preview_var).pack(side="left", padx=5)
        ttk.Label(footer, textvariable=self.total_files_found).pack(side="right", padx=5)

    def build_status_bar(self):
        status = tk.Frame(self.root, bg="#4d93c6", height=24)
        status.pack(fill="x", side="bottom")
        ttk.Button(status, text="Home", command=self.go_home).pack(side="left", padx=5)
        ttk.Label(status, text="Ready", background="#4d93c6", foreground="white").pack(side="left")

    def go_home(self):
        messagebox.showinfo("Home", "Returning to Home...")

    def toggle_select_all(self):
        if self.select_all_var.get():
            for item in self.file_table.get_children():
                self.file_table.selection_add(item)
        else:
            self.file_table.selection_remove(self.file_table.selection())

    def filter_file_table(self, *args):
        query = self.search_text.get().lower()
        self.file_table.delete(*self.file_table.get_children())
        for f, p, s, c in self.files:
            if query in f.lower() or query in p.lower():
                self.file_table.insert("", "end", values=(f, p, s, c))

    def start_scan(self):
        if not self.drive_table.selection():
            messagebox.showerror("Error", "Please select a drive.")
            return
        selected = self.drive_table.item(self.drive_table.selection()[0])["values"][0]
        self.selected_drive.set(selected)
        self.scan_progress.set(0)
        self.files = []
        self.file_table.delete(*self.file_table.get_children())
        self.stop_scan = False
        self.stop_btn.config(state="normal")
        self.scan_thread = threading.Thread(target=self.scan_drive)
        self.scan_thread.start()

    def cancel_scan(self):
        self.stop_scan = True
        self.stop_btn.config(state="disabled")

    def edit_custom_extensions(self):
        new_list = simpledialog.askstring("Edit Custom List", "Enter extensions separated by commas (e.g., .jpg,.png,.docx):")
        if new_list:
            self.custom_extensions = [ext.strip() for ext in new_list.split(",")]

    def scan_drive(self):
        drive = self.selected_drive.get()
        exts = {
            "[Pictures]": [".jpg", ".jpeg", ".png", ".bmp", ".gif"],
            "[Music]": [".mp3", ".wav", ".aac"],
            "[Documents]": [".txt", ".doc", ".docx", ".pdf"],
            "[Videos]": [".mp4", ".mkv", ".avi"],
            "[Compressed]": [".zip", ".rar", ".7z"],
            "[All Files]": None
        }
        selected_exts = self.custom_extensions if self.scan_custom_list.get() else exts.get(self.selected_category.get(), None)
        total = 0

        for root_dir, dirs, files in os.walk(drive):
            if self.stop_scan:
                break
            if not self.full_scan.get():
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if self.stop_scan:
                    break
                if not self.deep_scan.get() and file.startswith('.'):
                    continue
                if selected_exts and not any(file.lower().endswith(ext) for ext in selected_exts):
                    continue
                path = os.path.join(root_dir, file)
                try:
                    size_bytes = os.path.getsize(path)
                    size = f"{size_bytes / (1024 ** 2):.2f} MB"
                    self.files.append((file, path, size, "Good"))
                    self.root.after(0, lambda f=file, p=path, s=size: self.file_table.insert("", "end", values=(f, p, s, "Good")))
                    total += 1
                    self.scan_progress.set(total % 100)
                except:
                    continue
        self.total_files_found.set(f"Total Files: {total}")
        self.stop_btn.config(state="disabled")

    def on_file_select(self, event):
        if not self.show_preview_var.get():
            self.preview_label.config(text="Preview Disabled", image="")
            return
        selected = self.file_table.focus()
        if not selected:
            self.preview_label.config(text="No Preview Available", image="")
            return
        values = self.file_table.item(selected)['values']
        if not values or len(values) < 2:
            self.preview_label.config(text="No Preview Available", image="")
            return
        path = values[1]
        if path.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                img = Image.open(path)
                img.thumbnail((220, 220))
                img_tk = ImageTk.PhotoImage(img)
                self.preview_label.config(image=img_tk, text="")
                self.preview_label.image = img_tk
            except:
                self.preview_label.config(text="Image preview failed", image="")
        elif path.lower().endswith(".txt"):
            try:
                with open(path, "r", errors="ignore") as f:
                    content = f.read(500)
                self.preview_label.config(text=content, image="")
            except:
                self.preview_label.config(text="Text preview failed", image="")
        else:
            self.preview_label.config(text="Preview not supported", image="")

    def recover_files(self):
        recovery_folder = filedialog.askdirectory(title="Select Recovery Folder")
        if not recovery_folder:
            return
        recovered = 0
        for item in self.file_table.selection():
            values = self.file_table.item(item)['values']
            path = values[1]
            try:
                dest_path = os.path.join(recovery_folder, os.path.basename(path))
                shutil.copy(path, dest_path)
                recovered += 1
            except Exception as e:
                print(f"Failed to recover {path}: {e}")
        messagebox.showinfo("Recovery Complete", f"Recovered {recovered} file(s).")

if __name__ == '__main__':
    root = tk.Tk()
    app = RecoveryApp(root)
    root.mainloop()
