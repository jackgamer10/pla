import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import aiodns
import re
import os
import threading
import time
from provider_config import MX_PROVIDER_MAPPING

class EmailSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MagxxicVOT - Advanced Email Sorter v1.0")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e2e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#2e2e3e", foreground="white", fieldbackground="#2e2e3e", borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#313244", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', '#4e4e5e')])

        self.mail_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "sorted_output"))

        self.is_running = False
        self.stats = {provider: 0 for provider in set(MX_PROVIDER_MAPPING.values())}
        self.stats['Others(MX)'] = 0
        self.stats['Others(No_MX)'] = 0
        self.stats['Unknown'] = 0
        self.total_loaded = 0
        self.total_checked = 0

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e1e2e", pady=15)
        header_frame.pack(fill="x")
        title_label = tk.Label(header_frame, text="✦ MagxxicVOT - Advanced Email Sorter ✦", font=("Segoe UI", 16, "bold"), bg="#1e1e2e", fg="#cba6f7")
        title_label.pack()

        # File Selection
        file_frame = tk.Frame(self.root, bg="#181825", padx=20, pady=15, highlightbackground="#313244", highlightthickness=1)
        file_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(file_frame, text="Mail File:", bg="#181825", fg="#bac2de", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        tk.Entry(file_frame, textvariable=self.mail_file, width=65, bg="#313244", fg="white", borderwidth=0, insertbackground="white").grid(row=0, column=1, padx=10)
        tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#45475a", fg="white", relief="flat", padx=10).grid(row=0, column=2)

        tk.Label(file_frame, text="Output Dir:", bg="#181825", fg="#bac2de", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(file_frame, textvariable=self.output_dir, width=65, bg="#313244", fg="white", borderwidth=0, insertbackground="white").grid(row=1, column=1, padx=10)
        tk.Button(file_frame, text="Browse", command=self.browse_dir, bg="#45475a", fg="white", relief="flat", padx=10).grid(row=1, column=2)

        # Statistics Table
        table_frame = tk.Frame(self.root, bg="#1e1e2e", padx=20)
        table_frame.pack(fill="both", expand=True)

        columns = ("#", "Name", "Count", "Percent", "File")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("File", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialize table rows
        for i, provider in enumerate(sorted(self.stats.keys()), 1):
            self.tree.insert("", "end", iid=provider, values=(i, provider, 0, "0.0%", f"{provider.lower()}.txt"))

        # Footer / Controls
        footer_frame = tk.Frame(self.root, bg="#11111b", padx=20, pady=10)
        footer_frame.pack(fill="x", side="bottom")

        self.status_label = tk.Label(footer_frame, text="STATUS: IDLE", bg="#11111b", fg="#fab387", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(side="left")

        self.progress_label = tk.Label(footer_frame, text="CHECKED: 0 / 0", bg="#11111b", fg="#bac2de", font=("Segoe UI", 9))
        self.progress_label.pack(side="left", padx=30)

        self.btn_start = tk.Button(footer_frame, text="START", command=self.start_sorting, bg="#a6e3a1", fg="#11111b", width=12, font=("Segoe UI", 9, "bold"), relief="flat")
        self.btn_start.pack(side="right", padx=5)

        self.btn_stop = tk.Button(footer_frame, text="STOP", command=self.stop_sorting, bg="#f38ba8", fg="#11111b", width=12, font=("Segoe UI", 9, "bold"), relief="flat", state="disabled")
        self.btn_stop.pack(side="right", padx=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.mail_file.set(filename)

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def start_sorting(self):
        if not self.mail_file.get():
            messagebox.showerror("Error", "Please select a mail file.")
            return

        if self.is_running: return

        self.is_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="STATUS: RUNNING", fg="#a6e3a1")

        # Reset stats
        for p in self.stats: self.stats[p] = 0
        self.total_checked = 0
        self.update_gui_stats()

        threading.Thread(target=self.run_async_loop, daemon=True).start()

    def stop_sorting(self):
        self.is_running = False
        self.status_label.config(text="STATUS: STOPPING...", fg="#f38ba8")

    def run_async_loop(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.sort_emails())
            loop.close()
        except Exception as e:
            print(f"Error in async loop: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.finish_sorting)

    async def get_mx_record(self, domain, resolver):
        try:
            result = await resolver.query(domain, 'MX')
            return [str(rdata.host).lower() for rdata in result]
        except: return None

    def identify_provider(self, mx_records):
        if not mx_records: return 'Others(No_MX)'
        for mx in mx_records:
            for pattern, provider in MX_PROVIDER_MAPPING.items():
                if pattern in mx: return provider
        return 'Others(MX)'

    async def process_email(self, email, resolver, output_files, lock):
        match = re.search(r'@([\w\.-]+)', email)
        if not match:
            provider = 'Unknown'
        else:
            domain = match.group(1).lower()
            mx_records = await self.get_mx_record(domain, resolver)
            provider = self.identify_provider(mx_records)

        async with lock:
            self.stats[provider] += 1
            self.total_checked += 1

            if provider in output_files:
                output_files[provider].write(email + '\n')
                output_files[provider].flush()

        if self.total_checked % 5 == 0 or self.total_checked == self.total_loaded:
            self.root.after(0, self.update_gui_stats)

    async def sort_emails(self):
        email_file = self.mail_file.get()
        out_dir = self.output_dir.get()
        if not os.path.exists(out_dir): os.makedirs(out_dir)

        with open(email_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            self.total_loaded = len(lines)

        output_files = {}
        for p in self.stats.keys():
            output_files[p] = open(os.path.join(out_dir, f"{p.lower()}.txt"), 'w')

        resolver = aiodns.DNSResolver()
        lock = asyncio.Lock()
        concurrency = 50
        tasks = []

        for line in lines:
            if not self.is_running: break
            email = line.strip()
            if not email:
                self.total_loaded -= 1
                continue

            tasks.append(asyncio.create_task(self.process_email(email, resolver, output_files, lock)))

            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks: await asyncio.gather(*tasks)

        for f in output_files.values(): f.close()

    def update_gui_stats(self):
        for provider, count in self.stats.items():
            percent = (count / self.total_checked * 100) if self.total_checked > 0 else 0
            self.tree.set(provider, "Count", count)
            self.tree.set(provider, "Percent", f"{percent:.1f}%")

        self.progress_label.config(text=f"CHECKED: {self.total_checked} / {self.total_loaded}")

    def finish_sorting(self):
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        if not self.is_running and self.total_checked < self.total_loaded:
             self.status_label.config(text="STATUS: STOPPED", fg="#f38ba8")
        else:
            self.status_label.config(text="STATUS: FINISHED", fg="#a6e3a1")
            messagebox.showinfo("Success", "Email sorting completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSorterGUI(root)
    root.mainloop()
