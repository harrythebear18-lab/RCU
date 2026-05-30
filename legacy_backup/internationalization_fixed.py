#!/usr/bin/env python3
"""
Internationalization - Fixed Working Version
Simple internationalization and localization tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class Internationalization:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Internationalization")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'success': '#00ff88',
            'text': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # Current language
        self.current_language = 'en'
        
        # Translations
        self.translations = {}
        
        # Data file
        self.data_file = "internationalization_data.json"
        
        # Initialize
        self.init_translations()
        self.create_widgets()
        self.load_translations()
    
    def init_translations(self):
        """Initialize translations data"""
        if not os.path.exists(self.data_file):
            default_translations = {
                "en": {
                    "title": "Internationalization Manager",
                    "language": "Language",
                    "translations": "Translations",
                    "add_translation": "Add Translation",
                    "edit_translation": "Edit Translation",
                    "delete_translation": "Delete Translation",
                    "key": "Key",
                    "value": "Value",
                    "save": "Save",
                    "cancel": "Cancel",
                    "export": "Export",
                    "import": "Import",
                    "settings": "Settings",
                    "auto_detect": "Auto Detect Language",
                    "fallback_language": "Fallback Language",
                    "welcome": "Welcome to Internationalization Manager",
                    "no_translations": "No translations available",
                    "translation_added": "Translation added successfully",
                    "translation_updated": "Translation updated successfully",
                    "translation_deleted": "Translation deleted successfully"
                },
                "es": {
                    "title": "Gestor de Internacionalización",
                    "language": "Idioma",
                    "translations": "Traducciones",
                    "add_translation": "Añadir Traducción",
                    "edit_translation": "Editar Traducción",
                    "delete_translation": "Eliminar Traducción",
                    "key": "Clave",
                    "value": "Valor",
                    "save": "Guardar",
                    "cancel": "Cancelar",
                    "export": "Exportar",
                    "import": "Importar",
                    "settings": "Configuración",
                    "auto_detect": "Detectar Idioma Automáticamente",
                    "fallback_language": "Idioma de Respaldo",
                    "welcome": "Bienvenido al Gestor de Internacionalización",
                    "no_translations": "No hay traducciones disponibles",
                    "translation_added": "Traducción añadida exitosamente",
                    "translation_updated": "Traducción actualizada exitosamente",
                    "translation_deleted": "Traducción eliminada exitosamente"
                },
                "fr": {
                    "title": "Gestionnaire d'Internationalisation",
                    "language": "Langue",
                    "translations": "Traductions",
                    "add_translation": "Ajouter une Traduction",
                    "edit_translation": "Modifier la Traduction",
                    "delete_translation": "Supprimer la Traduction",
                    "key": "Clé",
                    "value": "Valeur",
                    "save": "Sauvegarder",
                    "cancel": "Annuler",
                    "export": "Exporter",
                    "import": "Importer",
                    "settings": "Paramètres",
                    "auto_detect": "Détecter la Langue Automatiquement",
                    "fallback_language": "Langue de Secours",
                    "welcome": "Bienvenue au Gestionnaire d'Internationalisation",
                    "no_translations": "Aucune traduction disponible",
                    "translation_added": "Traduction ajoutée avec succès",
                    "translation_updated": "Traduction mise à jour avec succès",
                    "translation_deleted": "Traduction supprimée avec succès"
                },
                "de": {
                    "title": "Internationalisierungs-Manager",
                    "language": "Sprache",
                    "translations": "Übersetzungen",
                    "add_translation": "Übersetzung hinzufügen",
                    "edit_translation": "Übersetzung bearbeiten",
                    "delete_translation": "Übersetzung löschen",
                    "key": "Schlüssel",
                    "value": "Wert",
                    "save": "Speichern",
                    "cancel": "Abbrechen",
                    "export": "Exportieren",
                    "import": "Importieren",
                    "settings": "Einstellungen",
                    "auto_detect": "Sprache automatisch erkennen",
                    "fallback_language": "Fallback-Sprache",
                    "welcome": "Willkommen beim Internationalisierungs-Manager",
                    "no_translations": "Keine Übersetzungen verfügbar",
                    "translation_added": "Übersetzung erfolgreich hinzugefügt",
                    "translation_updated": "Übersetzung erfolgreich aktualisiert",
                    "translation_deleted": "Übersetzung erfolgreich gelöscht"
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_translations, f, indent=2)
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="🌍 Internationalization Manager", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Language selector
        lang_frame = tk.Frame(header_frame, bg=self.colors['card'])
        lang_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(lang_frame, text="🌐 Language:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar(value='en')
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                         values=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh'], 
                                         state="readonly")
        self.language_combo.pack(side=tk.LEFT, padx=5)
        self.language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_translations_tab(notebook)
        self.create_languages_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_export_tab(notebook)
    
    def create_translations_tab(self, notebook):
        """Create translations management tab"""
        translations_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(translations_frame, text="📋 Translations")
        
        # Translations list
        translations_list_frame = tk.Frame(translations_frame, bg=self.colors['card'], relief='raised', bd=1)
        translations_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(translations_list_frame, text="📋 Translations", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Search bar
        search_frame = tk.Frame(translations_list_frame, bg=self.colors['card'])
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 Search:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.filter_translations)
        
        # Translations listbox with scrollbar
        translations_container = tk.Frame(translations_list_frame, bg=self.colors['card'])
        translations_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(translations_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.translations_listbox = tk.Listbox(translations_container, font=('Consolas', 11),
                                              bg=self.colors['bg'], fg=self.colors['text'],
                                              yscrollcommand=scrollbar.set)
        self.translations_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.translations_listbox.yview)
        
        # Translation actions
        translation_actions_frame = tk.Frame(translations_list_frame, bg=self.colors['card'])
        translation_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(translation_actions_frame, text="➕ Add",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.add_translation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(translation_actions_frame, text="✏️ Edit",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.edit_translation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(translation_actions_frame, text="🗑️ Delete",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.delete_translation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(translation_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_translations).pack(side=tk.LEFT, padx=5)
    
    def create_languages_tab(self, notebook):
        """Create languages management tab"""
        languages_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(languages_frame, text="🌐 Languages")
        
        # Languages display
        languages_display_frame = tk.Frame(languages_frame, bg=self.colors['card'], relief='raised', bd=1)
        languages_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(languages_display_frame, text="🌐 Supported Languages", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Languages grid
        languages_grid_frame = tk.Frame(languages_display_frame, bg=self.colors['card'])
        languages_grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Language info
        languages_info = [
            ("en", "English", "🇺🇸", "Default language"),
            ("es", "Spanish", "🇪🇸", "Español"),
            ("fr", "French", "🇫🇷", "Français"),
            ("de", "German", "🇩🇪", "Deutsch"),
            ("it", "Italian", "🇮🇹", "Italiano"),
            ("pt", "Portuguese", "🇵🇹", "Português"),
            ("ru", "Russian", "🇷🇺", "Русский"),
            ("ja", "Japanese", "🇯🇵", "日本語"),
            ("zh", "Chinese", "🇨🇳", "中文")
        ]
        
        for i, (code, name, flag, description) in enumerate(languages_info):
            row = i // 3
            col = i % 3
            
            lang_frame = tk.Frame(languages_grid_frame, bg=self.colors['card'], relief='raised', bd=1)
            lang_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            # Flag and name
            flag_label = tk.Label(lang_frame, text=flag, font=('Arial', 20),
                               fg=self.colors['text'], bg=self.colors['card'])
            flag_label.pack(pady=5)
            
            name_label = tk.Label(lang_frame, text=f"{name} ({code})", font=('Arial', 11, 'bold'),
                                fg=self.colors['primary'], bg=self.colors['card'])
            name_label.pack()
            
            desc_label = tk.Label(lang_frame, text=description, font=('Arial', 9),
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
            desc_label.pack(pady=2)
            
            # Translation count
            if code in self.translations:
                count = len(self.translations[code])
                count_label = tk.Label(lang_frame, text=f"{count} translations", font=('Arial', 9),
                                      fg=self.colors['secondary'], bg=self.colors['card'])
                count_label.pack(pady=2)
            else:
                missing_label = tk.Label(lang_frame, text="No translations", font=('Arial', 9),
                                        fg=self.colors['warning'], bg=self.colors['card'])
                missing_label.pack(pady=2)
            
            # Add language button
            if code not in self.translations:
                add_btn = tk.Button(lang_frame, text="➕ Add",
                                   font=('Arial', 9, 'bold'),
                                   bg=self.colors['success'], fg='white',
                                   relief='flat', cursor='hand2',
                                   command=lambda c=code: self.add_language(c))
                add_btn.pack(pady=5)
        
        # Configure grid weights
        for i in range(3):
            languages_grid_frame.columnconfigure(i, weight=1)
    
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings display
        settings_display_frame = tk.Frame(settings_frame, bg=self.colors['card'], relief='raised', bd=1)
        settings_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(settings_display_frame, text="⚙️ Internationalization Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Settings options
        settings_options_frame = tk.Frame(settings_display_frame, bg=self.colors['card'])
        settings_options_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Auto detect language
        self.auto_detect_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_options_frame, text="🔍 Auto-detect system language",
                      variable=self.auto_detect_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Fallback language
        fallback_frame = tk.Frame(settings_options_frame, bg=self.colors['card'])
        fallback_frame.pack(fill=tk.X, pady=5)
        tk.Label(fallback_frame, text="🌐 Fallback language:",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.fallback_var = tk.StringVar(value='en')
        fallback_combo = ttk.Combobox(fallback_frame, textvariable=self.fallback_var,
                                      values=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh'], 
                                      state="readonly")
        fallback_combo.pack(side=tk.RIGHT, padx=5)
        
        # Auto translate missing
        self.auto_translate_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_options_frame, text="🤖 Auto-translate missing keys",
                      variable=self.auto_translate_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Save button
        tk.Button(settings_display_frame, text="💾 Save Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_settings).pack(pady=20)
    
    def create_export_tab(self, notebook):
        """Create export tab"""
        export_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(export_frame, text="📤 Export/Import")
        
        # Export options
        export_options_frame = tk.Frame(export_frame, bg=self.colors['card'], relief='raised', bd=1)
        export_options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(export_options_frame, text="📤 Export Translations", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Export format
        format_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        format_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(format_frame, text="📄 Export format:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.export_format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(format_frame, textvariable=self.export_format_var,
                                   values=["json", "csv", "xml"], state="readonly")
        format_combo.pack(side=tk.RIGHT, padx=5)
        
        # Export options
        options_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.export_all_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🌐 Export all languages",
                      variable=self.export_all_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        self.include_metadata_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="📋 Include metadata",
                      variable=self.include_metadata_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        # Export button
        export_button_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        export_button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(export_button_frame, text="📤 Export",
                 font=('Arial', 12, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.export_translations).pack(fill=tk.X)
        
        # Import section
        import_options_frame = tk.Frame(export_frame, bg=self.colors['card'], relief='raised', bd=1)
        import_options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(import_options_frame, text="📥 Import Translations", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Import options
        import_options_subframe = tk.Frame(import_options_frame, bg=self.colors['card'])
        import_options_subframe.pack(fill=tk.X, pady=10, padx=20)
        
        self.merge_import_var = tk.BooleanVar(value=True)
        tk.Checkbutton(import_options_subframe, text="🔀 Merge with existing",
                      variable=self.merge_import_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        self.overwrite_import_var = tk.BooleanVar(value=False)
        tk.Checkbutton(import_options_subframe, text="🔄 Overwrite existing",
                      variable=self.overwrite_import_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        # Import button
        import_button_frame = tk.Frame(import_options_frame, bg=self.colors['card'])
        import_button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(import_button_frame, text="📥 Import",
                 font=('Arial', 12, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.import_translations).pack(fill=tk.X)
    
    def load_translations(self):
        """Load translations from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.translations = json.load(f)
            self.refresh_translations()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load translations: {e}")
    
    def change_language(self, event=None):
        """Change current language"""
        self.current_language = self.language_var.get()
        self.refresh_translations()
        messagebox.showinfo("Language Changed", f"Language changed to {self.current_language}")
    
    def get_translation(self, key, language=None):
        """Get translation for a key"""
        if language is None:
            language = self.current_language
        
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        elif 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        else:
            return key
    
    def refresh_translations(self):
        """Refresh translations list"""
        self.translations_listbox.delete(0, tk.END)
        
        if self.current_language in self.translations:
            translations = self.translations[self.current_language]
            search_term = self.search_var.get().lower()
            
            for key, value in translations.items():
                if search_term and search_term not in key.lower() and search_term not in value.lower():
                    continue
                
                display_text = f"{key}: {value}"
                self.translations_listbox.insert(tk.END, display_text)
        else:
            self.translations_listbox.insert(tk.END, "No translations available for this language")
    
    def filter_translations(self, event=None):
        """Filter translations based on search"""
        self.refresh_translations()
    
    def add_translation(self):
        """Add new translation"""
        self.translation_dialog = tk.Toplevel(self.root)
        self.translation_dialog.title("Add Translation")
        self.translation_dialog.geometry("400x300")
        self.translation_dialog.configure(bg=self.colors['bg'])
        
        # Key
        tk.Label(self.translation_dialog, text="🔑 Key:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.key_var = tk.StringVar()
        tk.Entry(self.translation_dialog, textvariable=self.key_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Value
        tk.Label(self.translation_dialog, text="📝 Value:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.value_var = tk.StringVar()
        tk.Entry(self.translation_dialog, textvariable=self.value_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Language
        tk.Label(self.translation_dialog, text="🌐 Language:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.dialog_language_var = tk.StringVar(value=self.current_language)
        ttk.Combobox(self.translation_dialog, textvariable=self.dialog_language_var,
                     values=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh'], 
                     state="readonly").pack(fill=tk.X, padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.translation_dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 Save",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_translation).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="❌ Cancel",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.translation_dialog.destroy).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def save_translation(self):
        """Save translation from dialog"""
        try:
            key = self.key_var.get()
            value = self.value_var.get()
            language = self.dialog_language_var.get()
            
            if not key or not value:
                messagebox.showerror("Error", "Please enter both key and value!")
                return
            
            if language not in self.translations:
                self.translations[language] = {}
            
            self.translations[language][key] = value
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(self.translations, f, indent=2)
            
            self.refresh_translations()
            self.translation_dialog.destroy()
            
            messagebox.showinfo("Success", "Translation added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save translation: {e}")
    
    def edit_translation(self):
        """Edit selected translation"""
        selection = self.translations_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a translation to edit!")
            return
        
        selected_text = self.translations_listbox.get(selection[0])
        if ":" not in selected_text:
            return
        
        key, value = selected_text.split(":", 1)
        
        # Create edit dialog
        self.translation_dialog = tk.Toplevel(self.root)
        self.translation_dialog.title("Edit Translation")
        self.translation_dialog.geometry("400x300")
        self.translation_dialog.configure(bg=self.colors['bg'])
        
        # Key (read-only)
        tk.Label(self.translation_dialog, text="🔑 Key:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.key_var = tk.StringVar(value=key.strip())
        tk.Entry(self.translation_dialog, textvariable=self.key_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'],
                state='readonly').pack(fill=tk.X, padx=20, pady=5)
        
        # Value
        tk.Label(self.translation_dialog, text="📝 Value:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.value_var = tk.StringVar(value=value.strip())
        tk.Entry(self.translation_dialog, textvariable=self.value_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Language
        tk.Label(self.translation_dialog, text="🌐 Language:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.dialog_language_var = tk.StringVar(value=self.current_language)
        ttk.Combobox(self.translation_dialog, textvariable=self.dialog_language_var,
                     values=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh'], 
                     state="readonly").pack(fill=tk.X, padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.translation_dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 Update",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.update_translation).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="❌ Cancel",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.translation_dialog.destroy).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def update_translation(self):
        """Update existing translation"""
        try:
            key = self.key_var.get()
            value = self.value_var.get()
            language = self.dialog_language_var.get()
            
            if not key or not value:
                messagebox.showerror("Error", "Please enter both key and value!")
                return
            
            if language not in self.translations:
                self.translations[language] = {}
            
            self.translations[language][key] = value
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(self.translations, f, indent=2)
            
            self.refresh_translations()
            self.translation_dialog.destroy()
            
            messagebox.showinfo("Success", "Translation updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update translation: {e}")
    
    def delete_translation(self):
        """Delete selected translation"""
        selection = self.translations_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a translation to delete!")
            return
        
        selected_text = self.translations_listbox.get(selection[0])
        if ":" not in selected_text:
            return
        
        key, value = selected_text.split(":", 1)
        key = key.strip()
        
        if messagebox.askyesno("Confirm Delete", f"Delete translation for key '{key}'?"):
            try:
                if self.current_language in self.translations and key in self.translations[self.current_language]:
                    del self.translations[self.current_language][key]
                    
                    # Save to file
                    with open(self.data_file, 'w') as f:
                        json.dump(self.translations, f, indent=2)
                    
                    self.refresh_translations()
                    messagebox.showinfo("Success", "Translation deleted successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete translation: {e}")
    
    def add_language(self, language_code):
        """Add new language"""
        if language_code not in self.translations:
            self.translations[language_code] = {}
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(self.translations, f, indent=2)
            
            messagebox.showinfo("Success", f"Language '{language_code}' added successfully!")
            self.refresh_translations()
    
    def save_settings(self):
        """Save internationalization settings"""
        try:
            settings = {
                "auto_detect": self.auto_detect_var.get(),
                "fallback_language": self.fallback_var.get(),
                "auto_translate": self.auto_translate_var.get(),
                "current_language": self.current_language
            }
            
            # Save settings to a separate file
            settings_file = "i18n_settings.json"
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def export_translations(self):
        """Export translations to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                export_format = self.export_format_var.get()
                
                if export_format == "json":
                    self.export_json(filename)
                elif export_format == "csv":
                    self.export_csv(filename)
                elif export_format == "xml":
                    self.export_xml(filename)
                
                messagebox.showinfo("Success", f"Translations exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export translations: {e}")
    
    def export_json(self, filename):
        """Export as JSON"""
        if self.export_all_var.get():
            data = self.translations
        else:
            data = {self.current_language: self.translations.get(self.current_language, {})}
        
        if self.include_metadata_var.get():
            data['_metadata'] = {
                'exported_at': datetime.now().isoformat(),
                'exported_by': 'Internationalization Manager',
                'languages': list(self.translations.keys())
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_csv(self, filename):
        """Export as CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Language', 'Key', 'Value'])
            
            languages = list(self.translations.keys()) if self.export_all_var.get() else [self.current_language]
            
            for lang in languages:
                if lang in self.translations:
                    for key, value in self.translations[lang].items():
                        writer.writerow([lang, key, value])
    
    def export_xml(self, filename):
        """Export as XML"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element('translations')
        
        languages = list(self.translations.keys()) if self.export_all_var.get() else [self.current_language]
        
        for lang in languages:
            if lang in self.translations:
                lang_elem = ET.SubElement(root, 'language', code=lang)
                for key, value in self.translations[lang].items():
                    trans_elem = ET.SubElement(lang_elem, 'translation')
                    trans_elem.set('key', key)
                    trans_elem.text = value
        
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
    
    def import_translations(self):
        """Import translations from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    self.import_json(filename)
                elif filename.endswith('.csv'):
                    self.import_csv(filename)
                elif filename.endswith('.xml'):
                    self.import_xml(filename)
                
                self.refresh_translations()
                messagebox.showinfo("Success", f"Translations imported from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import translations: {e}")
    
    def import_json(self, filename):
        """Import from JSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove metadata if present
        if '_metadata' in data:
            del data['_metadata']
        
        for lang, translations in data.items():
            if lang not in self.translations:
                self.translations[lang] = {}
            
            if self.merge_import_var.get():
                self.translations[lang].update(translations)
            else:
                self.translations[lang] = translations
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(self.translations, f, indent=2)
    
    def import_csv(self, filename):
        """Import from CSV"""
        import csv
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                lang = row['Language']
                key = row['Key']
                value = row['Value']
                
                if lang not in self.translations:
                    self.translations[lang] = {}
                
                if self.merge_import_var.get() or key not in self.translations[lang]:
                    self.translations[lang][key] = value
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(self.translations, f, indent=2)
    
    def import_xml(self, filename):
        """Import from XML"""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(filename)
        root = tree.getroot()
        
        for lang_elem in root.findall('language'):
            lang = lang_elem.get('code')
            
            if lang not in self.translations:
                self.translations[lang] = {}
            
            for trans_elem in lang_elem.findall('translation'):
                key = trans_elem.get('key')
                value = trans_elem.text or ''
                
                if self.merge_import_var.get() or key not in self.translations[lang]:
                    self.translations[lang][key] = value
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(self.translations, f, indent=2)

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = Internationalization(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting internationalization manager: {e}")

if __name__ == "__main__":
    main()
