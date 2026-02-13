import tkinter as tk
from tkinter import ttk, messagebox, Menu
import json
import os
from PIL import Image, ImageTk 
import locales 

# Configuración de ruta de imágenes
IMG_DIR = "img" 
IMG_EXTENSION = ".png" 
BANNER_FILENAME = "banner.png"

# --- CLASE DE LÓGICA Y DATOS ---
class Analyzer:
    def __init__(self, data_path, bans_path):
        self.data_path = data_path
        self.bans_path = bans_path
        self.data = {}
        self.ban_data = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    self.data = content.get('heroes', content)
            except json.JSONDecodeError:
                print(f"Error: JSON inválido en {self.data_path}")
        else:
            self.data = {}
            print(f"Error: No se encontró {self.data_path}")

        if os.path.exists(self.bans_path):
            try:
                with open(self.bans_path, 'r', encoding='utf-8') as f:
                    self.ban_data = json.load(f).get('popularity', {})
            except:
                self.ban_data = {}

    def get_sorted_heroes_for_bans(self):
        return sorted(self.data.keys(), key=lambda x: (self.ban_data.get(x, 0), x), reverse=True)

    def get_comp_stats(self, heroes_list):
        stats = {'total_poke': 0, 'sub_roles': {}}
        active_heroes = [h for h in heroes_list if h and h in self.data]
        
        for h in active_heroes:
            info = self.data[h]
            stats['total_poke'] += info.get('damage_profile', {}).get('poke', 1)
            s_role = info.get('sub_role', 'General')
            stats['sub_roles'][s_role] = stats['sub_roles'].get(s_role, 0) + 1
            
        return stats

    def calculate_score(self, hero_name, allies, enemies):
        if not hero_name or hero_name not in self.data: return 0
        
        hero_stats = self.data[hero_name]
        score = 0
        
        my_sub_role = hero_stats.get('sub_role', 'General')
        my_poke = hero_stats.get('damage_profile', {}).get('poke', 1)
        my_role = hero_stats.get('role', 'Damage')

        enemy_stats = self.get_comp_stats(enemies)
        enemy_poke = enemy_stats['total_poke']
        enemy_flankers = enemy_stats['sub_roles'].get('Flanker', 0)
        
        active_enemies = [e for e in enemies if e]
        active_allies = [a for a in allies if a and a != hero_name]
        
        counters = hero_stats.get('counters', {})
        countered_by = hero_stats.get('countered_by', {})
        synergies = hero_stats.get('synergies', {})

        for enemy in active_enemies:
            if enemy in counters: score += counters[enemy].get('score', 0) * 1.5 
            if enemy in countered_by: score -= countered_by[enemy].get('score', 0) * 1.5

        has_synergy = False
        for ally in active_allies:
            if ally in synergies:
                score += synergies[ally].get('score', 0)
                has_synergy = True

        if enemy_poke >= 12:
            if my_sub_role == "Stalwart": score += 2.0
            elif my_poke >= 4: score += 1.5
            elif my_role == "Damage" and my_poke < 2 and my_sub_role != "Flanker": score -= 1.5

        if enemy_flankers >= 2:
            if my_role == "Support":
                if my_sub_role in ["Survivor", "Tactician"]: score += 2.0
                elif my_sub_role == "Medic" and hero_stats.get('survivability', 0) < 3: score -= 2.0
            
            if hero_stats.get('weakness_profile', {}).get('cc_susceptibility', 0) < 3:
                if my_sub_role in ["Specialist", "Bruiser"]: score += 1.0

        if my_sub_role in ["Sharpshooter", "Stalwart"]: score += 0.5

        if hero_stats.get('team_dependency', 3) >= 4 and not has_synergy:
            score -= 1

        return round(score, 1)

    def get_recommendations(self, current_allies, enemies, bans, forced_idx=None):
        scores = []
        for i, name in enumerate(current_allies):
            val = self.calculate_score(name, current_allies, enemies) if name and name in self.data else -999
            scores.append((i, val))
        
        target_idx = forced_idx if forced_idx is not None else min(scores, key=lambda x: x[1])[0]
        
        if target_idx >= len(current_allies): return None, [], scores

        target_hero = current_allies[target_idx]
        
        if target_hero and target_hero in self.data:
            target_role = self.data[target_hero]['role']
        else:
            target_role = "Tank" if target_idx == 0 else ("Damage" if target_idx in [1, 2] else "Support")
        
        candidates = []
        other_allies = [h for i, h in enumerate(current_allies) if i != target_idx and h]

        for name, info in self.data.items():
            if (info['role'] == target_role and 
                name != target_hero and 
                name not in other_allies and 
                name not in bans):
                
                temp_allies = current_allies[:] 
                temp_allies[target_idx] = name
                candidates.append((name, self.calculate_score(name, temp_allies, enemies)))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return target_hero, candidates[:3], scores

    def get_tip(self, hero_name, lang='es'):
        if hero_name not in self.data: return locales.get_text(lang, 'no_tips')
        hero_data = self.data[hero_name]
        raw_tips = hero_data.get('tips', None)
        
        if isinstance(raw_tips, dict):
            return raw_tips.get(lang, raw_tips.get('es', locales.get_text(lang, 'no_tips')))
        if isinstance(raw_tips, str):
            return raw_tips
        if lang in hero_data:
            return hero_data[lang]
        if 'es' in hero_data:
            return hero_data['es']
        return locales.get_text(lang, 'no_tips')

    def generate_argument(self, hero_name, enemies, allies, lang='es'):
        info = self.data[hero_name]
        argumentos = []
        
        sub_role = info.get('sub_role', 'General')
        poke_val = info.get('damage_profile', {}).get('poke', 0)
        enemy_stats = self.get_comp_stats(enemies)

        if enemy_stats['total_poke'] >= 12 and (poke_val >= 4 or sub_role == "Stalwart"):
             msg = locales.get_text(lang, 'arg_poke_res').format(sub_role=sub_role)
             argumentos.append(msg)

        if enemy_stats['sub_roles'].get('Flanker', 0) >= 2 and sub_role in ["Survivor", "Bruiser"]:
             msg = locales.get_text(lang, 'arg_anti_dive').format(sub_role=sub_role)
             argumentos.append(msg)

        active_enemies = [e for e in enemies if e]
        counters = info.get('counters', {})
        
        for enemy in active_enemies:
            if enemy in counters:
                reason = counters[enemy].get('type', 'counter').replace('_', ' ')
                msg = locales.get_text(lang, 'arg_counter').format(enemy=enemy, reason=reason)
                argumentos.append(msg)

        if argumentos:
            return "\n".join(argumentos)
        else:
            return locales.get_text(lang, 'arg_solid').format(sub_role=sub_role)

    def get_hero_analysis(self, hero_name, allies, enemies, lang='es'):
        if not hero_name or hero_name not in self.data: return None
        info = self.data[hero_name]
        
        current_tip = self.get_tip(hero_name, lang)
        
        analysis = {
            "pros": [], "cons": [], "synergies": [],
            "tips": current_tip, 
            "archetype": info.get('archetype', []),
            "sub_role": info.get('sub_role', "General"),
            "health": info.get('health', "???"),
            "poke": info.get('damage_profile', {}).get('poke', 0)
        }

        active_enemies = [e for e in enemies if e]
        active_allies = [a for a in allies if a and a != hero_name]

        for enemy in active_enemies:
            if enemy in info.get('counters', {}): 
                analysis["pros"].append(locales.get_text(lang, 'pro_txt').format(enemy))
            if enemy in info.get('countered_by', {}): 
                analysis["cons"].append(locales.get_text(lang, 'con_txt').format(enemy))

        for ally in active_allies:
            if ally in info.get('synergies', {}): 
                analysis["synergies"].append(locales.get_text(lang, 'syn_txt').format(ally))
        
        return analysis

# --- INTERFAZ GRÁFICA ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Overwatch Comp Analyzer")
        self.root.minsize(950, 650) 
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.lang = 'en' 
        self.analyzer = Analyzer('data.json', 'bans.json')
        
        self.ban_vars, self.ban_combos = [], []
        self.ally_vars, self.ally_checks, self.ally_combos, self.ally_score_labels, self.ally_img_labels = [], [], [], [], []
        self.enemy_vars, self.enemy_combos, self.enemy_score_labels, self.enemy_img_labels = [], [], [], []
        
        self.image_cache = {} 
        self.menu_bar = None 
        
        self.setup_ui()
        self.create_menu() 
        self.update_live_stats()
        self.apply_language()

    def t(self, key):
        return locales.get_text(self.lang, key)

    def load_hero_icon(self, hero_name, size=(60, 60)):
        if not hero_name or hero_name == self.t("empty_slot"):
            cache_key = ("__PLACEHOLDER__", size)
            if cache_key in self.image_cache: return self.image_cache[cache_key]
            tk_image = ImageTk.PhotoImage(Image.new('RGB', size, color='#bdc3c7'))
            self.image_cache[cache_key] = tk_image
            return tk_image

        cache_key = (hero_name, size)
        if cache_key in self.image_cache: return self.image_cache[cache_key]

        clean_name = "".join(c for c in hero_name if c.isalnum())
        candidates = [
            hero_name.replace(":", " ").replace("/", ""),
            clean_name,
            hero_name.replace(" ", "-").replace(":", "-"),
            hero_name.lower()
        ]
        
        found_path = None
        for c in candidates:
            path = os.path.join(IMG_DIR, f"{c}{IMG_EXTENSION}")
            if os.path.exists(path):
                found_path = path
                break
        
        found_path = found_path or os.path.join(IMG_DIR, f"{candidates[0]}{IMG_EXTENSION}")

        try:
            pil_image = Image.open(found_path).resize(size, Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            tk_image = ImageTk.PhotoImage(Image.new('RGB', size, color='#7f8c8d'))
            
        self.image_cache[cache_key] = tk_image
        return tk_image

    def create_menu(self):
        # Menú superior (File, Help, etc.)
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        # Usamos self.t() aquí para que salga en el idioma correcto al inicio
        self.menu_bar.add_cascade(label=self.t("menu_help"), menu=self.help_menu)
        self.help_menu.add_command(label=self.t("help_title"), command=self.show_help)

    def show_help(self):
        # Ventana modal de ayuda
        help_win = tk.Toplevel(self.root)
        help_win.title(self.t("help_title"))
        help_win.geometry("500x400")
        
        content_frame = ttk.Frame(help_win, padding="20")
        content_frame.pack(fill="both", expand=True)
        
        lbl_text = ttk.Label(content_frame, text=self.t("help_text"), wraplength=460, justify="left", font=('Segoe UI', 10))
        lbl_text.pack(fill="both", expand=True)
        
        ttk.Button(content_frame, text=self.t("btn_close"), command=help_win.destroy).pack(pady=10)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        for i in range(11):
            main_frame.columnconfigure(i, weight=1)

        # HEADER
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=11, pady=(0, 10), sticky="ew")
        
        self.lbl_bans = ttk.Label(top_frame, text="", font=('Segoe UI', 10, 'bold'))
        self.lbl_bans.pack(side="left")

        self.btn_lang = ttk.Button(top_frame, text="EN", width=5, command=self.toggle_language)
        self.btn_lang.pack(side="right", padx=5)
        self.btn_reset = ttk.Button(top_frame, text="", width=10, command=self.reset_ui)
        self.btn_reset.pack(side="right", padx=5)

        # BANS
        ban_frame = ttk.Frame(main_frame)
        ban_frame.grid(row=1, column=0, columnspan=11)
        for i in range(4):
            var = tk.StringVar(value="")
            var.trace_add("write", lambda *args: self.update_live_stats())
            cb = ttk.Combobox(ban_frame, textvariable=var, width=15, state="readonly")
            cb.pack(side="left", padx=5)
            self.ban_vars.append(var); self.ban_combos.append(cb)

        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=11, sticky="ew", pady=15)

        # SCORE BOARD
        self.score_frame = ttk.Frame(main_frame, relief="groove", borderwidth=2, padding=5)
        self.score_frame.grid(row=3, column=0, columnspan=11, pady=(0, 20), sticky="ew")
        self.score_frame.columnconfigure(0, weight=1)
        self.score_frame.columnconfigure(4, weight=1)
        
        self.lbl_team_score_ally = ttk.Label(self.score_frame, text="", font=('Arial', 14, 'bold'), foreground="#27ae60")
        self.lbl_team_score_ally.pack(side="left", padx=20)
        
        self.lbl_vs = ttk.Label(self.score_frame, text="VS", font=('Arial', 10))
        self.lbl_vs.pack(side="left", expand=True)
        
        self.lbl_team_score_enemy = ttk.Label(self.score_frame, text="", font=('Arial', 14, 'bold'), foreground="#c0392b")
        self.lbl_team_score_enemy.pack(side="right", padx=20)

        # HEADERS EQUIPOS
        self.lbl_header_ally = ttk.Label(main_frame, text="", font=('Segoe UI', 11, 'bold'), foreground="#2980b9")
        self.lbl_header_ally.grid(row=4, column=0, columnspan=6)
        
        self.lbl_header_enemy = ttk.Label(main_frame, text="", font=('Segoe UI', 11, 'bold'), foreground="#c0392b")
        self.lbl_header_enemy.grid(row=4, column=7, columnspan=4)

        roles_config = [("Tank", "🛡️"), ("Damage", "⚔️"), ("Damage", "⚔️"), ("Support", "💉"), ("Support", "💉")]
        
        def create_hero_row(idx, role, icon):
            r = idx + 5
            ttk.Button(main_frame, text="🔍", width=3, command=lambda x=idx: self.open_spotlight_window(x)).grid(row=r, column=0, padx=2)
            ttk.Label(main_frame, text=icon).grid(row=r, column=1, sticky="e", padx=2)
            
            # Label imagen aliado con borde sólido
            lbl_img_a = tk.Label(main_frame, bg="#ecf0f1", width=40, height=40, relief="solid", bd=2)
            lbl_img_a.grid(row=r, column=2, padx=5, pady=2)
            self.ally_img_labels.append(lbl_img_a)

            a_var = tk.StringVar()
            a_var.trace_add("write", lambda *args: self.update_live_stats())
            a_cb = ttk.Combobox(main_frame, textvariable=a_var, state="readonly", width=16)
            a_cb.grid(row=r, column=3, pady=4)
            self.ally_vars.append(a_var); self.ally_combos.append((a_cb, role))
            
            a_lbl = tk.Label(main_frame, text="0.0", width=4, font=('Arial', 9, 'bold'), bg="#ecf0f1", relief="solid", borderwidth=1)
            a_lbl.grid(row=r, column=4, padx=5)
            self.ally_score_labels.append(a_lbl)
            
            c_var = tk.BooleanVar()
            tk.Checkbutton(main_frame, variable=c_var, text="🔄", cursor="hand2").grid(row=r, column=5, padx=5)
            self.ally_checks.append(c_var)

            ttk.Separator(main_frame, orient='vertical').grid(row=r, column=6, sticky="ns", padx=10)

            e_lbl = tk.Label(main_frame, text="0.0", width=4, font=('Arial', 9, 'bold'), bg="#ecf0f1", relief="solid", borderwidth=1)
            e_lbl.grid(row=r, column=7, padx=5)
            self.enemy_score_labels.append(e_lbl)

            e_var = tk.StringVar()
            e_var.trace_add("write", lambda *args: self.update_live_stats())
            e_cb = ttk.Combobox(main_frame, textvariable=e_var, state="readonly", width=16)
            e_cb.grid(row=r, column=8, pady=4)
            self.enemy_vars.append(e_var); self.enemy_combos.append((e_cb, role))
            
            # Label imagen enemigo con borde sólido
            lbl_img_e = tk.Label(main_frame, bg="#ecf0f1", width=40, height=40, relief="solid", bd=2)
            lbl_img_e.grid(row=r, column=9, padx=5, pady=2)
            self.enemy_img_labels.append(lbl_img_e)

            ttk.Label(main_frame, text=icon).grid(row=r, column=10, sticky="w", padx=2)

        for i, (role, icon) in enumerate(roles_config):
            create_hero_row(i, role, icon)

        # Botón de Análisis
        self.btn_analyze = ttk.Button(main_frame, text="", command=self.run_analysis)
        self.btn_analyze.grid(row=12, column=0, columnspan=11, pady=(25, 15), sticky="ew")

        # --- BANNER INFERIOR ---
        banner_path = os.path.join(IMG_DIR, BANNER_FILENAME)
        if os.path.exists(banner_path):
            try:
                # Carga simple. Para alta calidad, asegurarse que el PNG tenga el tamaño correcto (ej: 900x120)
                pil_banner = Image.open(banner_path)
                self.tk_banner = ImageTk.PhotoImage(pil_banner)
                
                banner_lbl = ttk.Label(main_frame, image=self.tk_banner, anchor="center")
                banner_lbl.grid(row=13, column=0, columnspan=11, sticky="ew", pady=(0, 0))
            except Exception as e:
                print(f"Error cargando banner: {e}")
        else:
            # Espacio vacío si no hay banner
            ttk.Label(main_frame, text="").grid(row=13, column=0, pady=10)

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'es' else 'es'
        self.apply_language()
        self.update_live_stats()

    def apply_language(self):
        self.root.title(self.t("app_title"))
        self.lbl_bans.config(text=self.t("bans_label"))
        self.btn_reset.config(text=self.t("btn_reset"))
        self.btn_lang.config(text=self.lang.upper()) 
        self.lbl_header_ally.config(text=self.t("team_ally"))
        self.lbl_header_enemy.config(text=self.t("team_enemy"))
        self.btn_analyze.config(text=self.t("btn_analyze"))
        self.lbl_vs.config(text=self.t("vs"))
        
        # Actualización de Menú: usamos index 1 porque en Tkinter el primer item 
        # añadido con add_cascade a veces se mapea al índice 1 (o 0 si no hay tearoff del sistema).
        # En tu código original usabas 1, así que lo mantenemos para ser consistente.
        if self.menu_bar:
            try:
                # Cambiamos el texto de "Ayuda" / "Help" en la barra principal
                self.menu_bar.entryconfigure(1, label=self.t("menu_help"))
                # Cambiamos el texto de "Guía" / "Guide" dentro del desplegable (índice 0)
                self.help_menu.entryconfigure(0, label=self.t("help_title"))
            except Exception as e:
                # Fallback por si acaso el índice cambia
                print(f"Menu update warning: {e}")

        self.update_live_stats()

    def reset_ui(self):
        empty_val = self.t("empty_slot")
        for v in self.ban_vars: v.set(empty_val)
        for v in self.ally_vars: v.set("")
        for v in self.enemy_vars: v.set("")
        for c in self.ally_checks: c.set(False)
        self.update_live_stats()

    def get_color_and_status(self, score):
        if score >= 1.5: return "#abebc6", "black" # Verde
        elif score <= -2.0: return "#e74c3c", "white" # Rojo
        return "#f9e79f", "black" # Amarillo

    def _update_combo_list(self, combo_list, vars_list, bans, all_sorted):
        for i, (cb, role) in enumerate(combo_list):
            others = [v.get() for j, v in enumerate(vars_list) if i != j and v.get()]
            available = [n for n in all_sorted 
                         if self.analyzer.data[n]['role'] == role and n not in (bans + others)]
            cb['values'] = sorted(available)

    def update_live_stats(self):
        empty_val = self.t("empty_slot")
        current_bans = [v.get() for v in self.ban_vars if v.get() and v.get() != empty_val]
        allies = [v.get() for v in self.ally_vars] 
        enemies = [v.get() for v in self.enemy_vars]
        all_sorted = list(self.analyzer.data.keys())

        # Update Bans
        ban_pool = self.analyzer.get_sorted_heroes_for_bans()
        for i, cb in enumerate(self.ban_combos):
            others = [v.get() for j, v in enumerate(self.ban_vars) if i != j and v.get() != empty_val]
            cb['values'] = [empty_val] + [h for h in ban_pool if h not in others]
            if self.ban_vars[i].get() == "": self.ban_vars[i].set(empty_val)

        # Update Combos
        self._update_combo_list(self.ally_combos, self.ally_vars, current_bans, all_sorted)
        self._update_combo_list(self.enemy_combos, self.enemy_vars, current_bans, all_sorted)

        # --- LOGICA DE ACTUALIZACIÓN DE IMÁGENES Y COLORES DE FONDO ---
        
        # 1. Aliados
        for i, var in enumerate(self.ally_vars):
            hero_name = var.get()
            img = self.load_hero_icon(hero_name, size=(40, 40))
            
            # Calcular color de fondo
            bg_color = "#ecf0f1" # Default gris
            if hero_name and hero_name in self.analyzer.data:
                score = self.analyzer.calculate_score(hero_name, allies, enemies)
                bg_color, _ = self.get_color_and_status(score)
            
            self.ally_img_labels[i].config(image=img, bg=bg_color)

        # 2. Enemigos (La puntuación del enemigo se ve desde SU perspectiva o la NUESTRA?)
        # Generalmente queremos ver si el enemigo es peligroso.
        # En la lógica actual, calculate_score evalúa la fuerza del héroe.
        for i, var in enumerate(self.enemy_vars):
            hero_name = var.get()
            img = self.load_hero_icon(hero_name, size=(40, 40))
            
            bg_color = "#ecf0f1"
            if hero_name and hero_name in self.analyzer.data:
                # Calculamos el score del enemigo contra NOSOTROS (allies)
                score = self.analyzer.calculate_score(hero_name, enemies, allies)
                bg_color, _ = self.get_color_and_status(score)
                
            self.enemy_img_labels[i].config(image=img, bg=bg_color)

        # Update Text Scores
        def update_labels(labels, team, opp_team):
            total = 0
            for i, name in enumerate(team):
                lbl = labels[i]
                if name and name in self.analyzer.data:
                    score = self.analyzer.calculate_score(name, team, opp_team)
                    total += score
                    bg, fg = self.get_color_and_status(score)
                    lbl.config(text=f"{score}", bg=bg, fg=fg)
                else:
                    lbl.config(text="-", bg="#ecf0f1", fg="black")
            return total

        total_ally = update_labels(self.ally_score_labels, allies, enemies)
        total_enemy = update_labels(self.enemy_score_labels, enemies, allies)

        self.lbl_team_score_ally.config(text=self.t("score_ally").format(round(total_ally, 1)))
        self.lbl_team_score_enemy.config(text=self.t("score_enemy").format(round(total_enemy, 1)))

    # --- VENTANA SPOTLIGHT ---
    def open_spotlight_window(self, index):
        hero_name = self.ally_vars[index].get()
        if not hero_name:
            messagebox.showinfo("Spotlight", self.t("msg_select_slot"))
            return

        allies = [v.get() for v in self.ally_vars]
        enemies = [v.get() for v in self.enemy_vars]
        empty_val = self.t("empty_slot")
        bans = [v.get() for v in self.ban_vars if v.get() != empty_val]

        analysis = self.analyzer.get_hero_analysis(hero_name, allies, enemies, self.lang)
        if not analysis: return
        
        current_score = self.analyzer.calculate_score(hero_name, allies, enemies)
        bg_color, _ = self.get_color_and_status(current_score)
        _, recs, _ = self.analyzer.get_recommendations(allies, enemies, bans, forced_idx=index)
        
        best_alt_name, best_alt_score = recs[0] if recs else (None, -99)
        
        spot_win = tk.Toplevel(self.root)
        spot_win.title(self.t("spot_title").format(hero_name))
        spot_win.geometry("500x700")

        visual_frame = tk.Frame(spot_win, bg="#ecf0f1", pady=15)
        visual_frame.pack(fill="x")
        img_current = self.load_hero_icon(hero_name, size=(80, 80))

        if best_alt_name and (best_alt_score > current_score + 1.0):
            img_suggested = self.load_hero_icon(best_alt_name, size=(80, 80))
            
            f_c = tk.Frame(visual_frame, bg="#ecf0f1")
            f_c.pack(side="left", expand=True)
            tk.Label(f_c, text=self.t("spot_current"), font=("Arial", 8), bg="#ecf0f1").pack()
            tk.Label(f_c, image=img_current, bg=bg_color, bd=3, relief="solid").pack(pady=5)
            tk.Label(f_c, text=f"{hero_name}\n({current_score})", font=("Arial", 10, "bold"), bg="#ecf0f1").pack()

            f_a = tk.Frame(visual_frame, bg="#ecf0f1")
            f_a.pack(side="left", padx=10)
            tk.Label(f_a, text="➡", font=("Arial", 30), bg="#ecf0f1", fg="#7f8c8d").pack()
            pts_txt = self.t("pts")
            tk.Label(f_a, text=f"+{round(best_alt_score - current_score, 1)} {pts_txt}", font=("Arial", 9, "bold"), fg="#27ae60", bg="#ecf0f1").pack()

            f_s = tk.Frame(visual_frame, bg="#ecf0f1")
            f_s.pack(side="left", expand=True)
            tk.Label(f_s, text=self.t("spot_better"), font=("Arial", 8, "bold"), fg="#27ae60", bg="#ecf0f1").pack()
            tk.Label(f_s, image=img_suggested, bg="#2ecc71", bd=3, relief="solid").pack(pady=5)
            tk.Label(f_s, text=f"{best_alt_name}\n({best_alt_score})", font=("Arial", 10, "bold"), bg="#ecf0f1").pack()
        else:
            tk.Label(visual_frame, text=self.t("spot_best_avail"), font=("Segoe UI", 10, "bold"), bg="#ecf0f1", fg="#27ae60").pack()
            tk.Label(visual_frame, image=img_current, bg=bg_color, bd=4, relief="solid").pack(pady=10)
            tk.Label(visual_frame, text=f"{hero_name} ({current_score})", font=("Arial", 14, "bold"), bg="#ecf0f1").pack()

        ttk.Separator(spot_win, orient='horizontal').pack(fill="x")

        content = ttk.Frame(spot_win, padding="15")
        content.pack(fill="both", expand=True)

        tf = ttk.LabelFrame(content, text=self.t("tech_data"), padding=5)
        tf.pack(fill="x", pady=(0, 10))
        
        tech_data = [
            (self.t("lbl_hp"), analysis['health'], "black"),
            (self.t("lbl_sub"), analysis['sub_role'], "#8e44ad"),
            (self.t("lbl_poke"), f"{'★' * int(analysis['poke'])} ({analysis['poke']}/5)", "#e67e22")
        ]
        
        for i, (label, val, color) in enumerate(tech_data):
            ttk.Label(tf, text=label, font=("Segoe UI", 9, "bold")).grid(row=0, column=i*2, sticky="e", padx=5)
            ttk.Label(tf, text=f"{val}", foreground=color).grid(row=0, column=i*2+1, sticky="w", padx=5)

        ttk.Label(content, text=f"Tags: {', '.join(analysis['archetype'])}", font=("Segoe UI", 9, "italic"), foreground="gray").pack(anchor="w", pady=(5, 10))

        for title, items, color in [(self.t("pros"), analysis['pros'] + analysis['synergies'], "#27ae60"), 
                                    (self.t("cons"), analysis['cons'], "#c0392b")]:
            if items:
                ttk.Label(content, text=title, font=("Segoe UI", 10, "bold"), foreground=color).pack(anchor="w")
                for it in items: ttk.Label(content, text=f"• {it}", wraplength=450).pack(anchor="w", padx=10)
                ttk.Separator(content, orient='horizontal').pack(fill="x", pady=8)

        ttk.Label(content, text=self.t("tips"), font=("Segoe UI", 10, "bold"), foreground="#f39c12").pack(anchor="w")
        ttk.Label(content, text=analysis['tips'], wraplength=460, justify="left").pack(anchor="w", padx=10, pady=2)
        
        spot_win.image_ref1 = img_current
        if 'img_suggested' in locals(): spot_win.image_ref2 = img_suggested
        
        ttk.Button(spot_win, text=self.t("btn_close"), command=spot_win.destroy).pack(pady=10)

    # --- VENTANA ANÁLISIS/REPORTE ---
    def run_analysis(self):
        allies = [v.get() for v in self.ally_vars]
        enemies = [v.get() for v in self.enemy_vars]
        empty_val = self.t("empty_slot")
        bans = [v.get() for v in self.ban_vars if v.get() != empty_val]
        forced = next((i for i, v in enumerate(self.ally_checks) if v.get()), None)
        
        target, recs, _ = self.analyzer.get_recommendations(allies, enemies, bans, forced)
        if target: self.show_report(target, recs, enemies, allies)
        else: messagebox.showinfo("Info", self.t("msg_no_rec"))

    def show_report(self, target, recs, enemies, allies):
        res_win = tk.Toplevel(self.root)
        res_win.title(self.t("rep_title").format(target))
        res_win.geometry("550x750")
        cont = ttk.Frame(res_win, padding="25")
        cont.pack(fill="both", expand=True)

        if not recs:
            ttk.Label(cont, text=self.t("rep_no_impr")).pack()
            return

        suggested_hero, suggested_score = recs[0]
        data = self.analyzer.data[suggested_hero]
        
        hf = ttk.Frame(cont)
        hf.pack(fill="x", pady=(0, 15))
        
        hf.columnconfigure(0, weight=1)
        hf.columnconfigure(1, weight=0)
        hf.columnconfigure(2, weight=1)

        img_curr = self.load_hero_icon(target, size=(70,70))
        f_left = ttk.Frame(hf)
        f_left.grid(row=0, column=0)
        ttk.Label(f_left, text="Current", font=('Arial', 8)).pack()
        tk.Label(f_left, image=img_curr, bg="#e74c3c", bd=2, relief="solid").pack(pady=2)
        ttk.Label(f_left, text=target if target else "Empty", font=('Arial', 9)).pack()

        ttk.Label(hf, text="➡", font=('Arial', 30, 'bold'), foreground="#7f8c8d").grid(row=0, column=1, padx=20)

        img_sugg = self.load_hero_icon(suggested_hero, size=(80,80))
        f_right = ttk.Frame(hf)
        f_right.grid(row=0, column=2)
        ttk.Label(f_right, text="Suggested", font=('Arial', 8, 'bold'), foreground="#27ae60").pack()
        tk.Label(f_right, image=img_sugg, bg="#2ecc71", bd=3, relief="solid").pack(pady=2)
        ttk.Label(f_right, text=suggested_hero, font=('Arial', 11, 'bold')).pack()

        sf = ttk.LabelFrame(cont, text=f" {self.t('tech_data').strip()} ", padding="10")
        sf.pack(fill="x", pady=5)
        stats_text = f"{self.t('lbl_sub')} {data.get('sub_role','Gen')} | HP: {data.get('health','?')} | {self.t('lbl_poke')} {data.get('damage_profile',{}).get('poke',0)}/5"
        ttk.Label(sf, text=stats_text, font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        
        ttk.Label(cont, text=self.t("rep_why"), font=('Segoe UI', 11, 'bold'), foreground="#2c3e50").pack(anchor="w", pady=(10, 5))
        arg_text = self.analyzer.generate_argument(suggested_hero, enemies, allies, self.lang)
        ttk.Label(cont, text=arg_text, font=('Segoe UI', 10), justify="left").pack(anchor="w")

        tf = ttk.Frame(cont, style="Tip.TFrame", padding="10", borderwidth=1, relief="solid")
        tf.pack(fill="x", pady=20)
        ttk.Label(tf, text=self.t("rep_tip_key"), font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        
        tip_text = self.analyzer.get_tip(suggested_hero, self.lang)
        ttk.Label(tf, text=tip_text, wraplength=480).pack(anchor="w")

        ttk.Separator(cont, orient='horizontal').pack(fill="x", pady=10)
        ttk.Label(cont, text=self.t("rep_others"), font=('Segoe UI', 9, 'bold'), foreground="gray").pack(anchor="w")
        for r_name, r_score in recs[1:]:
             ttk.Label(cont, text=f"• {r_name} (Score: {r_score})").pack(anchor="w")
        
        res_win.image_ref1 = img_curr
        res_win.image_ref2 = img_sugg
        
        ttk.Button(res_win, text=self.t("btn_close"), command=res_win.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam') 
    app = App(root)
    root.mainloop()