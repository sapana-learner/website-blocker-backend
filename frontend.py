import customtkinter as ctk
import requests
import platform
import subprocess
import threading

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
API_BASE = "https://website-blocker-backend-production.up.railway.app"

HOSTS_FILE = (
    r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows"
    else "/etc/hosts"
)
REDIRECT_IP = "127.0.0.1"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ──────────────────────────────────────────────
# HOSTS FILE HELPERS (run as admin/sudo)
# ──────────────────────────────────────────────
def block_website_locally(website: str):
    """Add website to system hosts file to block it."""
    try:
        with open(HOSTS_FILE, "r") as f:
            content = f.read()
        entry = f"{REDIRECT_IP} {website}"
        if entry not in content:
            with open(HOSTS_FILE, "a") as f:
                f.write(f"\n{entry}\n")
    except PermissionError:
        # On Mac/Linux, try with sudo via subprocess
        entry = f"{REDIRECT_IP} {website}"
        subprocess.run(
            ["sudo", "sh", "-c", f"echo '{entry}' >> {HOSTS_FILE}"],
            check=False
        )
    except Exception:
        pass


def unblock_all_locally(websites: list):
    """Remove all blocked websites from hosts file."""
    try:
        with open(HOSTS_FILE, "r") as f:
            lines = f.readlines()
        new_lines = [
            line for line in lines
            if not any(site in line for site in websites)
        ]
        with open(HOSTS_FILE, "w") as f:
            f.writelines(new_lines)
    except Exception:
        pass


# ──────────────────────────────────────────────
# LOGIN / REGISTER SCREEN
# ──────────────────────────────────────────────
class AuthScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FocusSpace – Login")
        self.geometry("450x550")
        self.resizable(False, False)

        self.user_id = None
        self.mode = "login"  # or "register"

        self._build_ui()

    def _build_ui(self):
        # Logo
        ctk.CTkLabel(self, text="🛡️ FocusSpace", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Your personal focus companion", text_color="gray").pack(pady=(0, 30))

        self.card = ctk.CTkFrame(self)
        self.card.pack(padx=40, fill="x")

        # Tab buttons
        self.tab_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.tab_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.login_tab = ctk.CTkButton(
            self.tab_frame, text="Login",
            command=lambda: self._switch_mode("login"),
            fg_color="#3498db", width=120
        )
        self.login_tab.pack(side="left", padx=(0, 10))

        self.register_tab = ctk.CTkButton(
            self.tab_frame, text="Register",
            command=lambda: self._switch_mode("register"),
            fg_color="transparent", width=120
        )
        self.register_tab.pack(side="left")

        # Name field (only for register)
        self.name_entry = ctk.CTkEntry(self.card, placeholder_text="Full Name", height=40)

        # Email + Password
        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", height=40)
        self.email_entry.pack(padx=20, pady=(10, 8), fill="x")

        self.password_entry = ctk.CTkEntry(self.card, placeholder_text="Password", show="*", height=40)
        self.password_entry.pack(padx=20, pady=(0, 8), fill="x")

        # Status message
        self.status_label = ctk.CTkLabel(self.card, text="", text_color="red")
        self.status_label.pack(pady=(0, 5))

        # Submit button
        self.submit_btn = ctk.CTkButton(
            self.card, text="Login", height=42,
            command=self._submit
        )
        self.submit_btn.pack(padx=20, pady=(5, 20), fill="x")

    def _switch_mode(self, mode: str):
        self.mode = mode
        if mode == "register":
            self.name_entry.pack(in_=self.card, padx=20, pady=(10, 8), fill="x",
                                  before=self.email_entry)
            self.login_tab.configure(fg_color="transparent")
            self.register_tab.configure(fg_color="#3498db")
            self.submit_btn.configure(text="Create Account")
            self.status_label.configure(text="")
        else:
            self.name_entry.pack_forget()
            self.login_tab.configure(fg_color="#3498db")
            self.register_tab.configure(fg_color="transparent")
            self.submit_btn.configure(text="Login")
            self.status_label.configure(text="")

    def _submit(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self.status_label.configure(text="Please fill in all fields.", text_color="red")
            return

        self.submit_btn.configure(state="disabled", text="Please wait...")

        def do_request():
            try:
                if self.mode == "login":
                    resp = requests.post(f"{API_BASE}/login", json={
                        "email": email, "password": password
                    }, timeout=10)
                    if resp.status_code == 200:
                        user_id = resp.json().get("user_id")
                        self.after(0, lambda: self._on_success(user_id))
                    else:
                        msg = resp.json().get("detail", "Login failed.")
                        self.after(0, lambda: self._on_error(msg))

                else:
                    name = self.name_entry.get().strip()
                    if not name:
                        self.after(0, lambda: self._on_error("Please enter your name."))
                        return
                    resp = requests.post(f"{API_BASE}/register", json={
                        "name": name, "email": email, "password": password
                    }, timeout=10)
                    if resp.status_code == 200:
                        self.after(0, lambda: self._on_error("Account created! Please login.", color="green"))
                        self.after(0, lambda: self._switch_mode("login"))
                    else:
                        msg = resp.json().get("detail", "Registration failed.")
                        self.after(0, lambda: self._on_error(msg))

            except requests.exceptions.ConnectionError:
                self.after(0, lambda: self._on_error("Cannot connect to server."))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=do_request, daemon=True).start()

    def _on_success(self, user_id):
        self.user_id = user_id
        self.destroy()

    def _on_error(self, message, color="red"):
        self.status_label.configure(text=message, text_color=color)
        self.submit_btn.configure(state="normal",
                                   text="Login" if self.mode == "login" else "Create Account")


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
class Dashboard(ctk.CTk):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.session_active = False
        self.blocked_sites = []

        self.title("FocusSpace Dashboard")
        self.geometry("900x580")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        self._load_websites()

    # ── Sidebar ──────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="🛡️ FocusSpace",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 30))

        ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", anchor="w"
                      ).grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(self.sidebar, text="Analytics", fg_color="transparent", anchor="w"
                      ).grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self.sidebar, text="Appearance:", anchor="w"
                     ).grid(row=5, column=0, padx=20, pady=(10, 0))

        ctk.CTkOptionMenu(
            self.sidebar, values=["Dark", "Light", "System"],
            command=lambda v: ctk.set_appearance_mode(v)
        ).grid(row=6, column=0, padx=20, pady=(10, 20))

    # ── Main Content ─────────────────────────
    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        self.main.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.main, text="Welcome Back 👋",
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Card 1 – Session Controller
        ctrl = ctk.CTkFrame(self.main)
        ctrl.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(ctrl, text="Session Controller",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=15, anchor="w")

        self.session_btn = ctk.CTkButton(
            ctrl, text="▶ Activate Blocklist",
            fg_color="#3498db", height=40,
            command=self._toggle_session
        )
        self.session_btn.pack(pady=20, padx=20, fill="x")

        self.session_status = ctk.CTkLabel(ctrl, text="Session: Inactive", text_color="gray")
        self.session_status.pack(pady=(0, 15))

        # Card 2 – Focus Score
        metric = ctk.CTkFrame(self.main)
        metric.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(metric, text="Daily Progress",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=15, anchor="w")

        ctk.CTkLabel(metric, text="85%",
                     font=ctk.CTkFont(size=48, weight="bold"),
                     text_color="#2ecc71").pack(pady=5)

        ctk.CTkLabel(metric, text="Focus Score Today", text_color="gray").pack(pady=(0, 15))

        # Card 3 – Blocked Websites
        list_card = ctk.CTkFrame(self.main)
        list_card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(list_card, text="Distraction Rules",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=15, anchor="w")

        entry_row = ctk.CTkFrame(list_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=15, pady=5)

        self.url_entry = ctk.CTkEntry(
            entry_row, placeholder_text="Enter website URL (e.g., youtube.com)"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(entry_row, text="Add", width=80,
                      command=self._add_website).pack(side="right")

        # Website list display
        self.sites_label = ctk.CTkLabel(list_card, text="Blocked sites: None", text_color="gray")
        self.sites_label.pack(pady=(5, 15), padx=15, anchor="w")

        # Status bar
        self.api_status = ctk.CTkLabel(self.main, text="", text_color="gray",
                                        font=ctk.CTkFont(size=11))
        self.api_status.grid(row=3, column=0, columnspan=2, pady=(5, 0))

    # ── Actions ──────────────────────────────
    def _toggle_session(self):
        self.session_btn.configure(state="disabled")

        def do_toggle():
            try:
                if not self.session_active:
                    resp = requests.post(f"{API_BASE}/start-focus", json={
                        "status": "ACTIVE", "user_id": self.user_id
                    }, timeout=10)
                    if resp.status_code == 200:
                        self.session_active = True
                        for site in self.blocked_sites:
                            block_website_locally(site)
                        self.after(0, self._update_session_ui)
                    else:
                        self.after(0, lambda: self._set_status("Failed to start session.", "red"))
                else:
                    resp = requests.post(
                        f"{API_BASE}/stop-focus?user_id={self.user_id}", timeout=10
                    )
                    if resp.status_code == 200:
                        self.session_active = False
                        unblock_all_locally(self.blocked_sites)
                        self.after(0, self._update_session_ui)
                    else:
                        self.after(0, lambda: self._set_status("Failed to stop session.", "red"))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", "red"))
            finally:
                self.after(0, lambda: self.session_btn.configure(state="normal"))

        threading.Thread(target=do_toggle, daemon=True).start()

    def _update_session_ui(self):
        if self.session_active:
            self.session_btn.configure(text="⏹ Deactivate Blocklist", fg_color="#e74c3c")
            self.session_status.configure(text="Session: ACTIVE 🔴", text_color="#e74c3c")
            self._set_status("Focus session started. Sites blocked locally.", "green")
        else:
            self.session_btn.configure(text="▶ Activate Blocklist", fg_color="#3498db")
            self.session_status.configure(text="Session: Inactive", text_color="gray")
            self._set_status("Session stopped. Sites unblocked.", "gray")

    def _add_website(self):
        website = self.url_entry.get().strip()
        if not website:
            self._set_status("Please enter a website URL.", "red")
            return

        self.url_entry.delete(0, "end")

        def do_add():
            try:
                resp = requests.post(f"{API_BASE}/add-website", json={
                    "website": website, "user_id": self.user_id
                }, timeout=10)
                if resp.status_code == 200:
                    self.blocked_sites.append(website)
                    if self.session_active:
                        block_website_locally(website)
                    self.after(0, self._update_sites_label)
                    self.after(0, lambda: self._set_status(f"Added {website}", "green"))
                else:
                    self.after(0, lambda: self._set_status("Failed to add website.", "red"))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", "red"))

        threading.Thread(target=do_add, daemon=True).start()

    def _load_websites(self):
        def do_load():
            try:
                resp = requests.get(f"{API_BASE}/websites/{self.user_id}", timeout=10)
                if resp.status_code == 200:
                    sites = [w["website"] for w in resp.json()]
                    self.blocked_sites = sites
                    self.after(0, self._update_sites_label)
            except Exception:
                pass

        threading.Thread(target=do_load, daemon=True).start()

    def _update_sites_label(self):
        if self.blocked_sites:
            sites_text = "Blocked: " + ", ".join(self.blocked_sites)
        else:
            sites_text = "Blocked sites: None"
        self.sites_label.configure(text=sites_text)

    def _set_status(self, msg, color="gray"):
        self.api_status.configure(text=msg, text_color=color)


# ──────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # Show login screen
    auth = AuthScreen()
    auth.mainloop()

    # If login succeeded, open dashboard
    if auth.user_id:
        dashboard = Dashboard(user_id=auth.user_id)
        dashboard.mainloop()
