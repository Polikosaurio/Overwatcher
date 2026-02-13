# locales.py

TRANSLATIONS = {
    "es": {
        "app_title": "OW2 Coach 2026 - Actualización Temp 1",
        "bans_label": "⛔ BANEOS",
        "team_ally": "TU EQUIPO",
        "team_enemy": "ENEMIGOS",
        "btn_analyze": "📊 SUGERIR MEJOR CAMBIO",
        "btn_reset": "🗑️ RESETEAR",
        "btn_lang": "ES",  # Indica el idioma actual
        "menu_options": "Opciones",
        "menu_theme": "Tema",
        "theme_light": "Claro (Estándar)",
        "theme_dark": "Azul Noche",
        "score_ally": "Aliados: {}",
        "score_enemy": "Enemigos: {}",
        "empty_slot": "--- VACÍO ---",
        "vs": "VS",
        "menu_help": "Ayuda",
        "help_title": "Guía de uso",
        "help_text": "¡Gracias por usar esta pequeña herramienta para conocer mejor a los personajes de Overwatch! Te recomiendo rellenar los héroes tanto de tu equipo como del equipo rival, utilizando las listas desplegables. Una vez hecho esto, podrás usar el botón 'Sugerir mejor cambio'. Si juegas en competitivo, no olvides también marcar los baneos con los desplegables superiores. Si no quieres rellenar ambos equipos y sólo quieres conocer opciones para un héroe, asegúrate al menos de tener un héroe en cada equipo, y usa el icono de lupa a su izquierda para buscar posibles alternativas al personaje elegido. Los héroes arrojan datos numéricos orientativos, y no reflejan la habilidad de los jugadores con los héroes. Si crees que un miembro de tu equipo no está desempeñando bien, puedes conseguir que el mejor cambio para el equipo priorice su rol, marcando para ello la cajita a la derecha de su nombre. Puedes usar la aplicación también en inglés con el botón de idioma actual 'EN/ES'. Arte del banner: Poliko - artstation.com/Poliko. Programado por Poliko asistido por un clanker.",
        
        # Analyzer & Logic
        "role_tank": "Tanque",
        "role_damage": "Daño",
        "role_support": "Apoyo",
        "arg_poke_res": "• Respuesta al Poke: [{sub_role} reduce presión a distancia].",
        "arg_anti_dive": "• Anti-Dive: [{sub_role} resiste el flanqueo agresivo].",
        "arg_counter": "• Ventaja vs {enemy}: [{reason}].",
        "arg_solid": "• Opción sólida como {sub_role}.",
        
        # Spotlight & Report
        "spot_title": "Spotlight 2026: {}",
        "spot_current": "ACTUAL",
        "spot_better": "MEJOR CAMBIO",
        "spot_best_avail": "✅ MEJOR OPCIÓN DISPONIBLE",
        "pts": "pts",
        "tech_data": " Datos Técnicos (2026) ",
        "lbl_hp": "HP Base:",
        "lbl_sub": "Sub-Rol:",
        "lbl_poke": "Poke:",
        "pros": "✅ Puntos Fuertes:",
        "cons": "⚠️ Riesgos Detectados:",
        "synergies": "🤝 Sinergias:",
        "tips": "💡 Tip Táctico:",
        "pro_txt": "Fuerte contra {}",
        "con_txt": "Amenazado por {}",
        "syn_txt": "Buena química con {}",
        "no_tips": "Sin consejos disponibles.",
        
        # Report Window
        "rep_title": "Estrategia: Reemplazando a {}",
        "rep_no_impr": "No se encontraron mejoras claras.",
        "rep_best_opt": "MEJOR OPCIÓN:",
        "rep_why": "\nPOR QUÉ ELEGIRLO:",
        "rep_tip_key": "💡 CONSEJO CLAVE",
        "rep_others": "Otras opciones viables:",
        "msg_select_slot": "Selecciona un héroe en este hueco primero.",
        "msg_no_rec": "No se pudo generar recomendación.",
        "btn_close": "Cerrar"
    },
    "en": {
        "app_title": "OW2 Coach 2026 - Season 1 Update",
        "bans_label": "⛔ BANS",
        "team_ally": "YOUR TEAM",
        "team_enemy": "ENEMIES",
        "btn_analyze": "📊 SUGGEST BEST SWAP",
        "btn_reset": "🗑️ RESET",
        "btn_lang": "EN", # Indicates current language
        "menu_options": "Options",
        "menu_theme": "Theme",
        "theme_light": "Light (Standard)",
        "theme_dark": "Night Blue",
        "score_ally": "Allies: {}",
        "score_enemy": "Enemies: {}",
        "empty_slot": "--- EMPTY ---",
        "vs": "VS",
        "menu_help": "Help",
        "help_title": "User Guide",
        "help_text": "Thank you for using this small tool to understand Overwatch characters better! I recommend filling in the heroes for both your team and the rival team using the dropdown lists. Once done, you can use the 'Suggest Best Swap' button. If you play competitive, don't forget to also mark bans using the top dropdowns. If you don't want to fill both teams and only want options for one hero, ensure at least one hero is selected in each team, and use the magnifying glass icon to their left to search for alternatives. The numbers are indicative and do not reflect player skill. If you think a teammate is underperforming, you can force the 'Best Swap' to prioritize their role by checking the box next to their name. If you are a fan of Cervantes, Spanish language is also available through the 'EN/ES' button. Banner art: Poliko - artstation.com/poliko . Programmed by Poliko assisted by a clanker.",
        
        # Analyzer & Logic
        "role_tank": "Tank",
        "role_damage": "Damage",
        "role_support": "Support",
        "arg_poke_res": "• Poke Response: [{sub_role} reduces ranged pressure].",
        "arg_anti_dive": "• Anti-Dive: [{sub_role} resists aggressive flanking].",
        "arg_counter": "• Advantage vs {enemy}: [{reason}].",
        "arg_solid": "• Solid option as {sub_role}.",
        
        # Spotlight & Report
        "spot_title": "Spotlight 2026: {}",
        "spot_current": "CURRENT",
        "spot_better": "BETTER SWAP",
        "spot_best_avail": "✅ BEST AVAILABLE OPTION",
        "pts": "pts",
        "tech_data": " Technical Data (2026) ",
        "lbl_hp": "Base HP:",
        "lbl_sub": "Sub-Role:",
        "lbl_poke": "Poke:",
        "pros": "✅ Strengths:",
        "cons": "⚠️ Detected Risks:",
        "synergies": "🤝 Synergies:",
        "tips": "💡 Tactical Tip:",
        "pro_txt": "Strong against {}",
        "con_txt": "Threatened by {}",
        "syn_txt": "Good chemistry with {}",
        "no_tips": "No tips available.",
        
        # Report Window
        "rep_title": "Strategy: Replacing {}",
        "rep_no_impr": "No clear improvements found.",
        "rep_best_opt": "BEST OPTION:",
        "rep_why": "\nWHY CHOOSE IT:",
        "rep_tip_key": "💡 KEY TIP",
        "rep_others": "Other viable options:",
        "msg_select_slot": "Select a hero in this slot first.",
        "msg_no_rec": "Could not generate recommendation.",
        "btn_close": "Close"
    }
}

def get_text(lang, key):
    """Retorna el texto según el idioma, o el key si no existe"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['es']).get(key, key)