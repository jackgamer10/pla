import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import asyncio
import aiodns
import re
import os
import threading
from provider_config import MX_PROVIDER_MAPPING
from sorter_utils import process_email_base
from activation_mgr import get_hwid, is_activated, activate
from branding import BANNER
import db_mgr

class EmailSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MagxxicVOT - Advanced Email Sorter v1.1 Ultra")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e2e")

        if not is_activated():
            self.show_activation_dialog()
            if not is_activated():
                self.root.destroy()
                return

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#2e2e3e", foreground="white", fieldbackground="#2e2e3e", borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#313244", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', '#4e4e5e')])

        self.mail_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "sorted_output"))

        self.is_running = False
        self.stats = {} # Dynamic stats
        self.total_loaded = 0
        self.total_checked = 0

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e1e2e", pady=5)
        header_frame.pack(fill="x")

        title_label = tk.Label(header_frame, text="MAGXXICVOT EMAIL SORTER ULTRA", font=("Segoe UI", 24, "bold"), bg="#1e1e2e", fg="#cba6f7")
        title_label.pack()

        subtitle_label = tk.Label(header_frame, text="✦ Fuzzy Matching | ML-Lite | SQL Backend | DNS Liveness ✦", font=("Segoe UI", 10, "italic"), bg="#1e1e2e", fg="#bac2de")
        subtitle_label.pack(pady=(0, 10))

        # File Selection
        file_frame = tk.Frame(self.root, bg="#181825", padx=20, pady=15, highlightbackground="#313244", highlightthickness=1)
        file_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(file_frame, text="Mail File:", bg="#181825", fg="#bac2de", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        tk.Entry(file_frame, textvariable=self.mail_file, width=75, bg="#313244", fg="white", borderwidth=0, insertbackground="white").grid(row=0, column=1, padx=10)
        tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#45475a", fg="white", relief="flat", padx=10).grid(row=0, column=2)

        tk.Label(file_frame, text="Output Dir:", bg="#181825", fg="#bac2de", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(file_frame, textvariable=self.output_dir, width=75, bg="#313244", fg="white", borderwidth=0, insertbackground="white").grid(row=1, column=1, padx=10)
        tk.Button(file_frame, text="Browse", command=self.browse_dir, bg="#45475a", fg="white", relief="flat", padx=10).grid(row=1, column=2)

        # Tabs for Stats and Logs
        self.tab_control = ttk.Notebook(self.root)

        self.tab_stats = tk.Frame(self.tab_control, bg="#1e1e2e")
        self.tab_logs = tk.Frame(self.tab_control, bg="#1e1e2e")

        self.tab_control.add(self.tab_stats, text=" Statistics ")
        self.tab_control.add(self.tab_logs, text=" Recent Activity ")
        self.tab_control.pack(expand=1, fill="both", padx=20)

        # Statistics Table
        columns = ("#", "Provider Category", "Count", "Percent")
        self.tree = ttk.Treeview(self.tab_stats, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("Provider Category", width=300, anchor="w")

        scrollbar = ttk.Scrollbar(self.tab_stats, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Logs / Activity Table (for Feedback)
        log_columns = ("Time", "Email", "Domain", "Identified As")
        self.log_tree = ttk.Treeview(self.tab_logs, columns=log_columns, show="headings")
        for col in log_columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150, anchor="w")
        self.log_tree.pack(side="left", fill="both", expand=True)

        # Context Menu for Logs
        self.log_menu = tk.Menu(self.root, tearoff=0, bg="#313244", fg="white", activebackground="#4e4e5e")
        self.log_menu.add_command(label="Override Provider for this Domain", command=self.override_provider)
        self.log_tree.bind("<Button-3>", self.show_log_menu)

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

        self.btn_feedback = tk.Button(footer_frame, text="MANAGE OVERRIDES", command=self.manage_overrides, bg="#89b4fa", fg="#11111b", width=18, font=("Segoe UI", 9, "bold"), relief="flat")
        self.btn_feedback.pack(side="right", padx=20)

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
        self.stats = {}
        self.total_checked = 0
        self.tree.delete(*self.tree.get_children())
        self.log_tree.delete(*self.log_tree.get_children())
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

    async def process_email(self, email, resolver, output_files, lock):
        provider = await process_email_base(email, resolver)

        async with lock:
            self.stats[provider] = self.stats.get(provider, 0) + 1
            self.total_checked += 1

            # Use base provider name for filename (strip suffixes like (Fuzzy))
            base_provider = provider.split('(')[0].strip()

            if base_provider not in output_files:
                out_dir = self.output_dir.get()
                filename = base_provider.replace('/', '_').replace(' ', '_').lower() + ".txt"
                output_files[base_provider] = open(os.path.join(out_dir, filename), 'a')

            output_files[base_provider].write(email + '\n')
            output_files[base_provider].flush()

        # Update log tree (sample)
        if self.total_checked % 10 == 0:
            import datetime
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            domain = email.split('@')[-1] if '@' in email else "N/A"
            self.root.after(0, lambda: self.log_tree.insert("", 0, values=(time_str, email, domain, provider)))
            # Keep only last 50 logs
            if len(self.log_tree.get_children()) > 50:
                self.log_tree.delete(self.log_tree.get_children()[-1])

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
            if self.tree.exists(provider):
                self.tree.set(provider, "Count", count)
                self.tree.set(provider, "Percent", f"{percent:.1f}%")
            else:
                idx = len(self.tree.get_children()) + 1
                self.tree.insert("", "end", iid=provider, values=(idx, provider, count, f"{percent:.1f}%"))

        self.progress_label.config(text=f"CHECKED: {self.total_checked} / {self.total_loaded}")

    def show_log_menu(self, event):
        item = self.log_tree.identify_row(event.y)
        if item:
            self.log_tree.selection_set(item)
            self.log_menu.post(event.x_root, event.y_root)

    def override_provider(self):
        selected = self.log_tree.selection()
        if not selected: return
        values = self.log_tree.item(selected[0], "values")
        domain = values[2]

        new_provider = simpledialog.askstring("Override", f"Enter new provider for domain {domain}:")
        if new_provider:
            db_mgr.save_domain_provider(domain, new_provider, source='user')
            messagebox.showinfo("Success", f"All future emails from {domain} will be sorted to {new_provider}")

    def manage_overrides(self):
        overrides = db_mgr.get_user_overrides()
        if not overrides:
            messagebox.showinfo("Overrides", "No user overrides found in database.")
            return

        msg = "\n".join([f"{d} -> {p}" for d, p in overrides.items()])
        messagebox.showinfo("User Overrides", f"Current Overrides:\n\n{msg}")

    def show_activation_dialog(self):
        activation_win = tk.Toplevel(self.root)
        activation_win.title("MagxxicVOT Activation")
        activation_win.geometry("500x300")
        activation_win.configure(bg="#1e1e2e")
        activation_win.grab_set()

        hwid = get_hwid()
        tk.Label(activation_win, text="Application Not Activated", font=("Arial", 14, "bold"), bg="#1e1e2e", fg="#f38ba8").pack(pady=10)
        tk.Label(activation_win, text="Your HWID:", bg="#1e1e2e", fg="white").pack()
        hwid_entry = tk.Entry(activation_win, width=40, bg="#313244", fg="white", justify="center")
        hwid_entry.insert(0, hwid)
        hwid_entry.config(state="readonly")
        hwid_entry.pack(pady=5)

        def copy_hwid():
            self.root.clipboard_clear()
            self.root.clipboard_append(hwid)
            messagebox.showinfo("Success", "HWID copied to clipboard!")

        tk.Button(activation_win, text="Copy HWID", command=copy_hwid, bg="#45475a", fg="white").pack()
        tk.Label(activation_win, text="Enter Activation Token:", bg="#1e1e2e", fg="white").pack(pady=(20, 0))
        token_entry = tk.Entry(activation_win, width=40, bg="#313244", fg="white", justify="center")
        token_entry.pack(pady=5)

        def attempt_activation():
            token = token_entry.get().strip()
            if activate(token):
                messagebox.showinfo("Success", "Application activated successfully!")
                activation_win.destroy()
            else:
                messagebox.showerror("Error", "Invalid activation token.")

        tk.Button(activation_win, text="ACTIVATE", command=attempt_activation, bg="#a6e3a1", fg="#1e1e2e", font=("Arial", 10, "bold"), width=15).pack(pady=10)
        self.root.wait_window(activation_win)

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
