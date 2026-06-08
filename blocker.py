import customtkinter as ctk

# 1. Global styling and appearance
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

class FocusSpaceApp(ctk.CTk):
    def _init_(self):
        super()._init_()

        # 2. Main Window Window Configuration
        self.title("FocusSpace Dashboard")
        self.geometry("900x550")
        self.resizable(False, False) 

        # 3. Setting up Layout Columns (0 = Sidebar, 1 = Main Content)
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)    

        # =================================================================
        # LEFT NAVIGATION PANEL (Sidebar)
        # =================================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        # Logo / Branding
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="🛡️ FocusSpace", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Sidebar Menu Items
        self.dash_btn = ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color="transparent", anchor="w")
        self.dash_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.analytics_btn = ctk.CTkButton(self.sidebar_frame, text="Analytics", fg_color="transparent", anchor="w")
        self.analytics_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Dark/Light Mode Theme Switcher
        self.appearance_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance:", anchor="w")
        self.appearance_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # =================================================================
        # RIGHT MAIN PANEL (Content Canvas)
        # =================================================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        # Dashboard Header Welcome
        self.header_label = ctk.CTkLabel(
            self.main_frame, text="Welcome Back, Student", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # ---- Widget Card 1: Session Actions ----
        self.control_card = ctk.CTkFrame(self.main_frame)
        self.control_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.card1_title = ctk.CTkLabel(self.control_card, text="Session Controller", font=ctk.CTkFont(size=16, weight="bold"))
        self.card1_title.pack(pady=15, padx=15, anchor="w")
        
        self.toggle_session_btn = ctk.CTkButton(self.control_card, text="Activate Blocklist", fg_color="#3498db", height=40)
        self.toggle_session_btn.pack(pady=20, padx=20, fill="x")

        # ---- Widget Card 2: Metrics Dashboard ----
        self.metric_card = ctk.CTkFrame(self.main_frame)
        self.metric_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.card2_title = ctk.CTkLabel(self.metric_card, text="Daily Progress", font=ctk.CTkFont(size=16, weight="bold"))
        self.card2_title.pack(pady=15, padx=15, anchor="w")
        
        self.score_label = ctk.CTkLabel(self.metric_card, text="85%", font=ctk.CTkFont(size=48, weight="bold"), text_color="#2ecc71")
        self.score_label.pack(pady=5)
        
        self.score_sub = ctk.CTkLabel(self.metric_card, text="Focus Score Today", text_color="gray")
        self.score_sub.pack(pady=(0, 15))

        # ---- Widget Card 3: URL Inputs ----
        self.list_card = ctk.CTkFrame(self.main_frame)
        self.list_card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.card3_title = ctk.CTkLabel(self.list_card, text="Distraction Rules", font=ctk.CTkFont(size=16, weight="bold"))
        self.card3_title.pack(pady=10, padx=15, anchor="w")

        self.entry_row = ctk.CTkFrame(self.list_card, fg_color="transparent")
        self.entry_row.pack(fill="x", padx=15, pady=5)
        
        self.url_entry = ctk.CTkEntry(self.entry_row, placeholder_text="Enter website URL (e.g., youtube.com)")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.add_btn = ctk.CTkButton(self.entry_row, text="Add Target", width=100)
        self.add_btn.pack(side="right")

        self.spacer = ctk.CTkLabel(self.list_card, text="", height=10)
        self.spacer.pack()

    # Dynamic backend listener for theme switches
    def change_theme(self, selected_theme: str):
        ctk.set_appearance_mode(selected_theme)

if _name_ == "_main_":
    app = FocusSpaceApp()
    app.mainloop()
