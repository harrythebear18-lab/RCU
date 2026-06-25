#!/usr/bin/env python3
"""
Internationalization Framework
Multi-language support for the Windows 11 Resource Optimization System.
"""

import json
import os
import locale
from typing import Dict, Any, Optional
import tkinter as tk
from datetime import datetime
import re

class I18nManager:
    """Internationalization Manager for multi-language support"""
    
    def __init__(self, default_language: str = 'en'):
        self.current_language = default_language
        self.default_language = default_language
        self.translations = {}
        self.fallback_translations = {}
        self.supported_languages = {}
        
        # Language file paths
        self.languages_dir = os.path.join(os.path.dirname(__file__), 'languages')
        self.current_language_file = os.path.join(os.path.dirname(__file__), 'current_language.json')
        
        # Initialize language system
        self.initialize_languages()
        self.load_current_language()
        self.load_translations()
    
    def initialize_languages(self):
        """Initialize supported languages"""
        self.supported_languages = {
            'en': {
                'name': 'English',
                'native_name': 'English',
                'code': 'en-US',
                'flag': '🇺🇸',
                'rtl': False
            },
            'es': {
                'name': 'Spanish',
                'native_name': 'Español',
                'code': 'es-ES',
                'flag': '🇪🇸',
                'rtl': False
            },
            'fr': {
                'name': 'French',
                'native_name': 'Français',
                'code': 'fr-FR',
                'flag': '🇫🇷',
                'rtl': False
            },
            'de': {
                'name': 'German',
                'native_name': 'Deutsch',
                'code': 'de-DE',
                'flag': '🇩🇪',
                'rtl': False
            },
            'it': {
                'name': 'Italian',
                'native_name': 'Italiano',
                'code': 'it-IT',
                'flag': '🇮🇹',
                'rtl': False
            },
            'pt': {
                'name': 'Portuguese',
                'native_name': 'Português',
                'code': 'pt-BR',
                'flag': '🇧🇷',
                'rtl': False
            },
            'ru': {
                'name': 'Russian',
                'native_name': 'Русский',
                'code': 'ru-RU',
                'flag': '🇷🇺',
                'rtl': False
            },
            'ja': {
                'name': 'Japanese',
                'native_name': '日本語',
                'code': 'ja-JP',
                'flag': '🇯🇵',
                'rtl': False
            },
            'zh': {
                'name': 'Chinese',
                'native_name': '中文',
                'code': 'zh-CN',
                'flag': '🇨🇳',
                'rtl': False
            },
            'ar': {
                'name': 'Arabic',
                'native_name': 'العربية',
                'code': 'ar-SA',
                'flag': '🇸🇦',
                'rtl': True
            }
        }
        
        # Create languages directory if it doesn't exist
        os.makedirs(self.languages_dir, exist_ok=True)
        
        # Create default language files if they don't exist
        self.create_default_translations()
    
    def create_default_translations(self):
        """Create default translation files"""
        # English translations (default)
        en_translations = {
            # General UI
            'app_title': 'Windows 11 Resource Optimization System',
            'file': 'File',
            'edit': 'Edit',
            'view': 'View',
            'tools': 'Tools',
            'help': 'Help',
            'settings': 'Settings',
            'about': 'About',
            'exit': 'Exit',
            'save': 'Save',
            'cancel': 'Cancel',
            'ok': 'OK',
            'yes': 'Yes',
            'no': 'No',
            'apply': 'Apply',
            'reset': 'Reset',
            'refresh': 'Refresh',
            'close': 'Close',
            
            # System Dashboard
            'system_dashboard': 'System Dashboard',
            'cpu_usage': 'CPU Usage',
            'memory_usage': 'Memory Usage',
            'gpu_usage': 'GPU Usage',
            'disk_usage': 'Disk Usage',
            'network_usage': 'Network Usage',
            'temperature': 'Temperature',
            'processes': 'Processes',
            'services': 'Services',
            'performance': 'Performance',
            'optimization': 'Optimization',
            
            # Overclocking
            'overclocking_dashboard': 'Overclocking Dashboard',
            'cpu_overclock': 'CPU Overclock',
            'gpu_overclock': 'GPU Overclock',
            'ram_overclock': 'RAM Overclock',
            'stock': 'Stock',
            'gaming': 'Gaming',
            'performance': 'Performance',
            'extreme': 'Extreme',
            'insane': 'Insane',
            'suicide': 'Suicide',
            'warning': 'Warning',
            'danger': 'Danger',
            'safety_warning': 'Safety Warning',
            
            # Resource Optimizer
            'resource_optimizer': 'Resource Optimizer',
            'soft_clean': 'Soft Clean',
            'aggressive_clean': 'Aggressive Clean',
            'deep_clean': 'Deep Clean',
            'memory_jolt': 'Memory Jolt',
            'cpu_cleanup': 'CPU Cleanup',
            'gpu_cleanup': 'GPU Cleanup',
            'ram_cleanup': 'RAM Cleanup',
            
            # Settings
            'general_settings': 'General Settings',
            'alert_settings': 'Alert Settings',
            'performance_settings': 'Performance Settings',
            'theme': 'Theme',
            'language': 'Language',
            'update_interval': 'Update Interval',
            'enable_notifications': 'Enable Notifications',
            'cpu_threshold': 'CPU Threshold',
            'memory_threshold': 'Memory Threshold',
            'gpu_threshold': 'GPU Threshold',
            'temperature_threshold': 'Temperature Threshold',
            
            # Notifications
            'high_cpu_usage': 'High CPU Usage',
            'high_memory_usage': 'High Memory Usage',
            'high_gpu_usage': 'High GPU Usage',
            'high_temperature': 'High Temperature',
            'low_disk_space': 'Low Disk Space',
            'system_alert': 'System Alert',
            'performance_warning': 'Performance Warning',
            
            # Reports
            'performance_reports': 'Performance Reports',
            'daily_report': 'Daily Report',
            'weekly_report': 'Weekly Report',
            'export_report': 'Export Report',
            'health_score': 'Health Score',
            'recommendations': 'Recommendations',
            'trend_analysis': 'Trend Analysis',
            
            # Backup
            'backup_manager': 'Backup Manager',
            'create_backup': 'Create Backup',
            'restore_backup': 'Restore Backup',
            'backup_settings': 'Backup Settings',
            'auto_backup': 'Auto Backup',
            'backup_success': 'Backup Successful',
            'backup_failed': 'Backup Failed',
            
            # API
            'api_server': 'API Server',
            'api_status': 'API Status',
            'api_endpoints': 'API Endpoints',
            'api_key': 'API Key',
            'port': 'Port',
            'host': 'Host',
            
            # Messages
            'loading': 'Loading...',
            'processing': 'Processing...',
            'completed': 'Completed',
            'failed': 'Failed',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            'info': 'Information',
            
            # Time formats
            'seconds': 'seconds',
            'minutes': 'minutes',
            'hours': 'hours',
            'days': 'days',
            'weeks': 'weeks',
            'months': 'months',
            'years': 'years',
            'ago': 'ago',
            'remaining': 'remaining',
            
            # Units
            'percent': '%',
            'ghz': 'GHz',
            'mhz': 'MHz',
            'gb': 'GB',
            'mb': 'MB',
            'kb': 'KB',
            'celsius': '°C',
            'fahrenheit': '°F',
            
            # Status
            'healthy': 'Healthy',
            'warning': 'Warning',
            'critical': 'Critical',
            'unknown': 'Unknown',
            'active': 'Active',
            'inactive': 'Inactive',
            'running': 'Running',
            'stopped': 'Stopped',
            'pending': 'Pending',
            'completed': 'Completed'
        }
        
        # Save English translations
        en_file = os.path.join(self.languages_dir, 'en.json')
        with open(en_file, 'w', encoding='utf-8') as f:
            json.dump(en_translations, f, indent=2, ensure_ascii=False)
        
        # Spanish translations
        es_translations = {
            'app_title': 'Sistema de Optimización de Recursos de Windows 11',
            'file': 'Archivo',
            'edit': 'Editar',
            'view': 'Ver',
            'tools': 'Herramientas',
            'help': 'Ayuda',
            'settings': 'Configuración',
            'about': 'Acerca de',
            'exit': 'Salir',
            'save': 'Guardar',
            'cancel': 'Cancelar',
            'ok': 'OK',
            'yes': 'Sí',
            'no': 'No',
            'apply': 'Aplicar',
            'reset': 'Restablecer',
            'refresh': 'Actualizar',
            'close': 'Cerrar',
            'system_dashboard': 'Panel del Sistema',
            'cpu_usage': 'Uso de CPU',
            'memory_usage': 'Uso de Memoria',
            'gpu_usage': 'Uso de GPU',
            'disk_usage': 'Uso de Disco',
            'network_usage': 'Uso de Red',
            'temperature': 'Temperatura',
            'processes': 'Procesos',
            'services': 'Servicios',
            'performance': 'Rendimiento',
            'optimization': 'Optimización',
            'overclocking_dashboard': 'Panel de Overclocking',
            'cpu_overclock': 'Overclock de CPU',
            'gpu_overclock': 'Overclock de GPU',
            'ram_overclock': 'Overclock de RAM',
            'stock': 'Estándar',
            'gaming': 'Gaming',
            'performance': 'Rendimiento',
            'extreme': 'Extremo',
            'insane': 'Insano',
            'suicide': 'Suicida',
            'warning': 'Advertencia',
            'danger': 'Peligro',
            'safety_warning': 'Advertencia de Seguridad',
            'resource_optimizer': 'Optimizador de Recursos',
            'soft_clean': 'Limpieza Suave',
            'aggressive_clean': 'Limpieza Agresiva',
            'deep_clean': 'Limpieza Profunda',
            'memory_jolt': 'Impulso de Memoria',
            'cpu_cleanup': 'Limpieza de CPU',
            'gpu_cleanup': 'Limpieza de GPU',
            'ram_cleanup': 'Limpieza de RAM',
            'general_settings': 'Configuración General',
            'alert_settings': 'Configuración de Alertas',
            'performance_settings': 'Configuración de Rendimiento',
            'theme': 'Tema',
            'language': 'Idioma',
            'update_interval': 'Intervalo de Actualización',
            'enable_notifications': 'Habilitar Notificaciones',
            'cpu_threshold': 'Umbral de CPU',
            'memory_threshold': 'Umbral de Memoria',
            'gpu_threshold': 'Umbral de GPU',
            'temperature_threshold': 'Umbral de Temperatura',
            'high_cpu_usage': 'Alto Uso de CPU',
            'high_memory_usage': 'Alto Uso de Memoria',
            'high_gpu_usage': 'Alto Uso de GPU',
            'high_temperature': 'Alta Temperatura',
            'low_disk_space': 'Espacio en Disco Bajo',
            'system_alert': 'Alerta del Sistema',
            'performance_warning': 'Advertencia de Rendimiento',
            'performance_reports': 'Informes de Rendimiento',
            'daily_report': 'Informe Diario',
            'weekly_report': 'Informe Semanal',
            'export_report': 'Exportar Informe',
            'health_score': 'Puntuación de Salud',
            'recommendations': 'Recomendaciones',
            'trend_analysis': 'Análisis de Tendencias',
            'backup_manager': 'Gestor de Copias de Seguridad',
            'create_backup': 'Crear Copia de Seguridad',
            'restore_backup': 'Restaurar Copia de Seguridad',
            'backup_settings': 'Configuración de Copia de Seguridad',
            'auto_backup': 'Copia de Seguridad Automática',
            'backup_success': 'Copia de Seguridad Exitosa',
            'backup_failed': 'Copia de Seguridad Fallida',
            'api_server': 'Servidor API',
            'api_status': 'Estado de API',
            'api_endpoints': 'Endpoints de API',
            'api_key': 'Clave de API',
            'port': 'Puerto',
            'host': 'Host',
            'loading': 'Cargando...',
            'processing': 'Procesando...',
            'completed': 'Completado',
            'failed': 'Fallido',
            'error': 'Error',
            'success': 'Éxito',
            'warning': 'Advertencia',
            'info': 'Información',
            'seconds': 'segundos',
            'minutes': 'minutos',
            'hours': 'horas',
            'days': 'días',
            'weeks': 'semanas',
            'months': 'meses',
            'years': 'años',
            'ago': 'hace',
            'remaining': 'restante',
            'percent': '%',
            'ghz': 'GHz',
            'mhz': 'MHz',
            'gb': 'GB',
            'mb': 'MB',
            'kb': 'KB',
            'celsius': '°C',
            'fahrenheit': '°F',
            'healthy': 'Saludable',
            'warning': 'Advertencia',
            'critical': 'Crítico',
            'unknown': 'Desconocido',
            'active': 'Activo',
            'inactive': 'Inactivo',
            'running': 'Ejecutándose',
            'stopped': 'Detenido',
            'pending': 'Pendiente',
            'completed': 'Completado'
        }
        
        # Save Spanish translations
        es_file = os.path.join(self.languages_dir, 'es.json')
        with open(es_file, 'w', encoding='utf-8') as f:
            json.dump(es_translations, f, indent=2, ensure_ascii=False)
        
        # French translations
        fr_translations = {
            'app_title': 'Système d\'Optimisation des Ressources Windows 11',
            'file': 'Fichier',
            'edit': 'Éditer',
            'view': 'Affichage',
            'tools': 'Outils',
            'help': 'Aide',
            'settings': 'Paramètres',
            'about': 'À propos',
            'exit': 'Quitter',
            'save': 'Enregistrer',
            'cancel': 'Annuler',
            'ok': 'OK',
            'yes': 'Oui',
            'no': 'Non',
            'apply': 'Appliquer',
            'reset': 'Réinitialiser',
            'refresh': 'Actualiser',
            'close': 'Fermer',
            'system_dashboard': 'Tableau de Bord du Système',
            'cpu_usage': 'Utilisation CPU',
            'memory_usage': 'Utilisation Mémoire',
            'gpu_usage': 'Utilisation GPU',
            'disk_usage': 'Utilisation Disque',
            'network_usage': 'Utilisation Réseau',
            'temperature': 'Température',
            'processes': 'Processus',
            'services': 'Services',
            'performance': 'Performance',
            'optimization': 'Optimisation',
            'overclocking_dashboard': 'Tableau de Bord Overclocking',
            'cpu_overclock': 'Overclock CPU',
            'gpu_overclock': 'Overclock GPU',
            'ram_overclock': 'Overclock RAM',
            'stock': 'Stock',
            'gaming': 'Gaming',
            'performance': 'Performance',
            'extreme': 'Extrême',
            'insane': 'Insane',
            'suicide': 'Suicide',
            'warning': 'Avertissement',
            'danger': 'Danger',
            'safety_warning': 'Avertissement de Sécurité',
            'resource_optimizer': 'Optimiseur de Ressources',
            'soft_clean': 'Nettoyage Doux',
            'aggressive_clean': 'Nettoyage Aggressif',
            'deep_clean': 'Nettoyage Profond',
            'memory_jolt': 'Secousse Mémoire',
            'cpu_cleanup': 'Nettoyage CPU',
            'gpu_cleanup': 'Nettoyage GPU',
            'ram_cleanup': 'Nettoyage RAM',
            'general_settings': 'Paramètres Généraux',
            'alert_settings': 'Paramètres d\'Alerte',
            'performance_settings': 'Paramètres de Performance',
            'theme': 'Thème',
            'language': 'Langue',
            'update_interval': 'Intervalle de Mise à Jour',
            'enable_notifications': 'Activer les Notifications',
            'cpu_threshold': 'Seuil CPU',
            'memory_threshold': 'Seuil Mémoire',
            'gpu_threshold': 'Seuil GPU',
            'temperature_threshold': 'Seuil Température',
            'high_cpu_usage': 'Utilisation CPU Élevée',
            'high_memory_usage': 'Utilisation Mémoire Élevée',
            'high_gpu_usage': 'Utilisation GPU Élevée',
            'high_temperature': 'Température Élevée',
            'low_disk_space': 'Espace Disque Faible',
            'system_alert': 'Alerte Système',
            'performance_warning': 'Avertissement Performance',
            'performance_reports': 'Rapports de Performance',
            'daily_report': 'Rapport Quotidien',
            'weekly_report': 'Rapport Hebdomadaire',
            'export_report': 'Exporter le Rapport',
            'health_score': 'Score de Santé',
            'recommendations': 'Recommandations',
            'trend_analysis': 'Analyse de Tendance',
            'backup_manager': 'Gestionnaire de Sauvegarde',
            'create_backup': 'Créer une Sauvegarde',
            'restore_backup': 'Restaurer une Sauvegarde',
            'backup_settings': 'Paramètres de Sauvegarde',
            'auto_backup': 'Sauvegarde Automatique',
            'backup_success': 'Sauvegarde Réussie',
            'backup_failed': 'Sauvegarde Échouée',
            'api_server': 'Serveur API',
            'api_status': 'Statut API',
            'api_endpoints': 'Endpoints API',
            'api_key': 'Clé API',
            'port': 'Port',
            'host': 'Hôte',
            'loading': 'Chargement...',
            'processing': 'Traitement...',
            'completed': 'Terminé',
            'failed': 'Échoué',
            'error': 'Erreur',
            'success': 'Succès',
            'warning': 'Avertissement',
            'info': 'Information',
            'seconds': 'secondes',
            'minutes': 'minutes',
            'hours': 'heures',
            'days': 'jours',
            'weeks': 'semaines',
            'months': 'mois',
            'years': 'années',
            'ago': 'il y a',
            'remaining': 'restant',
            'percent': '%',
            'ghz': 'GHz',
            'mhz': 'MHz',
            'gb': 'GB',
            'mb': 'MB',
            'kb': 'KB',
            'celsius': '°C',
            'fahrenheit': '°F',
            'healthy': 'Sain',
            'warning': 'Avertissement',
            'critical': 'Critique',
            'unknown': 'Inconnu',
            'active': 'Actif',
            'inactive': 'Inactif',
            'running': 'En cours',
            'stopped': 'Arrêté',
            'pending': 'En attente',
            'completed': 'Terminé'
        }
        
        # Save French translations
        fr_file = os.path.join(self.languages_dir, 'fr.json')
        with open(fr_file, 'w', encoding='utf-8') as f:
            json.dump(fr_translations, f, indent=2, ensure_ascii=False)
    
    def load_current_language(self):
        """Load current language from settings"""
        try:
            if os.path.exists(self.current_language_file):
                with open(self.current_language_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_language = data.get('language', self.default_language)
            else:
                # Detect system language
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    lang_code = system_locale.split('_')[0].lower()
                    if lang_code in self.supported_languages:
                        self.current_language = lang_code
                        self.save_current_language()
        except Exception:
            self.current_language = self.default_language
    
    def save_current_language(self):
        """Save current language to settings"""
        try:
            data = {'language': self.current_language}
            with open(self.current_language_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def load_translations(self):
        """Load translations for current language"""
        try:
            # Load current language translations
            lang_file = os.path.join(self.languages_dir, f'{self.current_language}.json')
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            
            # Load fallback (English) translations
            fallback_file = os.path.join(self.languages_dir, f'{self.default_language}.json')
            if os.path.exists(fallback_file):
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.fallback_translations = json.load(f)
        except Exception:
            self.translations = {}
            self.fallback_translations = {}
    
    def translate(self, key: str, **kwargs) -> str:
        """Translate a key to the current language"""
        # Try current language first
        if key in self.translations:
            text = self.translations[key]
        elif key in self.fallback_translations:
            text = self.fallback_translations[key]
        else:
            return key  # Return key if no translation found
        
        # Handle string formatting
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return text
    
    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Get supported languages"""
        return self.supported_languages
    
    def set_language(self, language_code: str) -> bool:
        """Set current language"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            self.load_translations()
            self.save_current_language()
            return True
        return False
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """Get language information"""
        return self.supported_languages.get(language_code)
    
    def format_datetime(self, dt: datetime, format_type: str = 'medium') -> str:
        """Format datetime according to current language"""
        try:
            # Simple formatting based on language
            if self.current_language == 'en':
                if format_type == 'short':
                    return dt.strftime('%m/%d/%Y %H:%M')
                elif format_type == 'medium':
                    return dt.strftime('%b %d, %Y %I:%M %p')
                else:  # long
                    return dt.strftime('%A, %B %d, %Y at %I:%M:%S %p')
            elif self.current_language == 'es':
                if format_type == 'short':
                    return dt.strftime('%d/%m/%Y %H:%M')
                elif format_type == 'medium':
                    return dt.strftime('%d de %b de %Y %H:%M')
                else:  # long
                    return dt.strftime('%A, %d de %B de %Y a las %H:%M:%S')
            elif self.current_language == 'fr':
                if format_type == 'short':
                    return dt.strftime('%d/%m/%Y %H:%M')
                elif format_type == 'medium':
                    return dt.strftime('%d %b %Y %H:%M')
                else:  # long
                    return dt.strftime('%A %d %B %Y à %H:%M:%S')
            else:
                # Default to English format
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def format_number(self, number: float, decimal_places: int = 2) -> str:
        """Format number according to current language"""
        try:
            if self.current_language in ['de', 'fr', 'es', 'it']:
                # Use comma as decimal separator
                return f"{number:.{decimal_places}f}".replace('.', ',')
            else:
                # Use period as decimal separator
                return f"{number:.{decimal_places}f}"
        except Exception:
            return str(number)
    
    def is_rtl(self) -> bool:
        """Check if current language is right-to-left"""
        lang_info = self.supported_languages.get(self.current_language, {})
        return lang_info.get('rtl', False)

# Global I18n manager instance
i18n = I18nManager()

# Translation function for easy use
def t(key: str, **kwargs) -> str:
    """Translation function"""
    return i18n.translate(key, **kwargs)

# Language selection dialog
class LanguageSelectionDialog:
    """Language selection dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """Show language selection dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Language / Seleccione Idioma / Choisissez la Langue")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create UI
        self.create_ui()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
    
    def create_ui(self):
        """Create dialog UI"""
        # Title
        title_label = tk.Label(self.dialog, text="Select Language / Seleccione Idioma / Choisissez la Langue",
                               font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=20)
        
        # Language list
        languages_frame = tk.Frame(self.dialog)
        languages_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(languages_frame)
        scrollbar = tk.Scrollbar(languages_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add language buttons
        supported_languages = i18n.get_supported_languages()
        current_language = i18n.get_current_language()
        
        for lang_code, lang_info in supported_languages.items():
            btn_frame = tk.Frame(scrollable_frame)
            btn_frame.pack(fill=tk.X, pady=5)
            
            # Language button
            btn_text = f"{lang_info['flag']} {lang_info['native_name']} ({lang_info['name']})"
            
            bg_color = '#e3f2fd' if lang_code == current_language else '#ffffff'
            
            btn = tk.Button(btn_frame, text=btn_text, font=('Segoe UI', 10),
                           bg=bg_color, fg='black', relief='flat', bd=1,
                           command=lambda l=lang_code: self.select_language(l))
            btn.pack(fill=tk.X, padx=10, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def select_language(self, language_code: str):
        """Select language"""
        self.result = language_code
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel selection"""
        self.dialog.destroy()

if __name__ == '__main__':
    # Test internationalization
    print("Testing Internationalization Framework")
    print(f"Current language: {i18n.get_current_language()}")
    print(f"Supported languages: {list(i18n.get_supported_languages().keys())}")
    
    # Test translations
    print(f"English: {i18n.translate('app_title')}")
    
    # Test language switching
    i18n.set_language('es')
    print(f"Spanish: {i18n.translate('app_title')}")
    
    i18n.set_language('fr')
    print(f"French: {i18n.translate('app_title')}")
    
    # Test number formatting
    i18n.set_language('en')
    print(f"English number: {i18n.format_number(1234.56)}")
    
    i18n.set_language('de')
    print(f"German number: {i18n.format_number(1234.56)}")
    
    # Test datetime formatting
    from datetime import datetime
    now = datetime.now()
    print(f"English date: {i18n.format_datetime(now)}")
    
    i18n.set_language('es')
    print(f"Spanish date: {i18n.format_datetime(now)}")
