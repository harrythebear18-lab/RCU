#!/usr/bin/env python3
"""
Accessibility Features
Screen reader support, high contrast mode, and accessibility enhancements.
"""

import tkinter as tk
from tkinter import ttk, font
import json
import os
from typing import Dict, Any, Optional, Callable
import threading
import time
import win32com.client
import win32con
import win32api
import pywintypes

class AccessibilityManager:
    """Accessibility Manager for enhanced user experience"""
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(__file__), 'accessibility_settings.json')
        self.settings = self.load_settings()
        
        # Accessibility features
        self.high_contrast_mode = self.settings.get('high_contrast', False)
        self.screen_reader_enabled = self.settings.get('screen_reader', False)
        self.keyboard_navigation = self.settings.get('keyboard_navigation', True)
        self.font_size_multiplier = self.settings.get('font_size_multiplier', 1.0)
        self.color_blind_mode = self.settings.get('color_blind_mode', 'none')
        
        # Color schemes
        self.color_schemes = {
            'default': {
                'bg': '#1a1a1a',
                'card': '#2d2d2d',
                'primary': '#00d4ff',
                'success': '#00ff88',
                'warning': '#ffaa00',
                'danger': '#ff4444',
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent': '#ff6b6b'
            },
            'high_contrast': {
                'bg': '#000000',
                'card': '#000000',
                'primary': '#ffffff',
                'success': '#00ff00',
                'warning': '#ffff00',
                'danger': '#ff0000',
                'text': '#ffffff',
                'text_secondary': '#cccccc',
                'border': '#ffffff',
                'accent': '#ffffff'
            },
            'high_contrast_white': {
                'bg': '#ffffff',
                'card': '#ffffff',
                'primary': '#000000',
                'success': '#008000',
                'warning': '#ff8c00',
                'danger': '#ff0000',
                'text': '#000000',
                'text_secondary': '#333333',
                'border': '#000000',
                'accent': '#000000'
            },
            'protanopia': {
                'bg': '#1a1a1a',
                'card': '#2d2d2d',
                'primary': '#00b4d8',  # Blue instead of red
                'success': '#00ff88',
                'warning': '#ffaa00',
                'danger': '#00b4d8',  # Blue instead of red
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent': '#00b4d8'
            },
            'deuteranopia': {
                'bg': '#1a1a1a',
                'card': '#2d2d2d',
                'primary': '#00d4ff',
                'success': '#00ff88',
                'warning': '#ffaa00',
                'danger': '#ffaa00',  # Yellow instead of red
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent': '#ffaa00'
            },
            'tritanopia': {
                'bg': '#1a1a1a',
                'card': '#2d2d2d',
                'primary': '#ff6b6b',  # Pink instead of blue
                'success': '#00ff88',
                'warning': '#ffaa00',
                'danger': '#ff6b6b',  # Pink instead of red
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent': '#ff6b6b'
            }
        }
        
        # Font sizes
        self.base_font_sizes = {
            'small': 8,
            'normal': 10,
            'medium': 12,
            'large': 14,
            'xlarge': 16,
            'xxlarge': 18
        }
        
        # Keyboard navigation state
        self.keyboard_focus_widget = None
        self.tab_order = []
        self.current_tab_index = 0
        
        # Screen reader
        self.screen_reader = None
        if self.screen_reader_enabled:
            self.init_screen_reader()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load accessibility settings"""
        default_settings = {
            'high_contrast': False,
            'screen_reader': False,
            'keyboard_navigation': True,
            'font_size_multiplier': 1.0,
            'color_blind_mode': 'none',
            'focus_indicators': True,
            'reduced_motion': False,
            'high_visibility': False,
            'tooltips_enabled': True,
            'announcements_enabled': True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception:
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save accessibility settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_color_scheme(self) -> Dict[str, str]:
        """Get current color scheme"""
        if self.high_contrast_mode:
            return self.color_schemes['high_contrast']
        elif self.color_blind_mode != 'none':
            return self.color_schemes.get(self.color_blind_mode, self.color_schemes['default'])
        else:
            return self.color_schemes['default']
    
    def get_font_size(self, base_size: int) -> int:
        """Get adjusted font size"""
        return int(base_size * self.font_size_multiplier)
    
    def init_screen_reader(self):
        """Initialize screen reader support"""
        try:
            # Try to initialize Windows screen reader
            self.screen_reader = win32com.client.Dispatch("SAPI.SpVoice")
            self.screen_reader.Rate = 0  # Normal speed
            self.screen_reader.Volume = 100  # Full volume
        except Exception:
            self.screen_reader = None
    
    def speak(self, text: str, interrupt: bool = False):
        """Speak text using screen reader"""
        if not self.screen_reader_enabled or not self.screen_reader:
            return
        
        try:
            if interrupt:
                self.screen_reader.Speak(text, 1)  # SPF_ASYNC
            else:
                self.screen_reader.Speak(text, 0)  # SPF_DEFAULT
        except Exception:
            pass
    
    def announce_widget(self, widget: tk.Widget, action: str = "focused"):
        """Announce widget information"""
        if not self.announcements_enabled:
            return
        
        text = ""
        
        # Get widget type
        widget_class = widget.winfo_class()
        
        # Get widget text
        if hasattr(widget, 'cget'):
            try:
                if widget_class in ['Button', 'Label', 'Checkbutton', 'Radiobutton']:
                    text = widget.cget('text')
                elif widget_class == 'Entry':
                    text = f"Entry: {widget.get()}"
                elif widget_class == 'Scale':
                    text = f"Slider: {widget.get()}"
                elif widget_class == 'Combobox':
                    text = f"Combo box: {widget.get()}"
            except:
                pass
        
        # Create announcement
        if text:
            announcement = f"{action} {widget_class} {text}"
        else:
            announcement = f"{action} {widget_class}"
        
        self.speak(announcement)
    
    def set_high_contrast(self, enabled: bool):
        """Enable/disable high contrast mode"""
        self.high_contrast_mode = enabled
        self.save_settings({'high_contrast': enabled})
        
        # Apply high contrast to system if available
        try:
            if enabled:
                # Set Windows high contrast mode
                win32api.SystemParametersInfo(win32con.SPI_SETHIGHCONTRAST, 0, None)
            else:
                # Reset Windows high contrast mode
                win32api.SystemParametersInfo(win32con.SPI_SETHIGHCONTRAST, 0, None)
        except Exception:
            pass
    
    def set_color_blind_mode(self, mode: str):
        """Set color blind mode"""
        valid_modes = ['none', 'protanopia', 'deuteranopia', 'tritanopia']
        if mode in valid_modes:
            self.color_blind_mode = mode
            self.save_settings({'color_blind_mode': mode})
    
    def set_font_size_multiplier(self, multiplier: float):
        """Set font size multiplier"""
        if 0.5 <= multiplier <= 3.0:
            self.font_size_multiplier = multiplier
            self.save_settings({'font_size_multiplier': multiplier})
    
    def set_screen_reader(self, enabled: bool):
        """Enable/disable screen reader"""
        self.screen_reader_enabled = enabled
        self.save_settings({'screen_reader': enabled})
        
        if enabled and not self.screen_reader:
            self.init_screen_reader()
    
    def enhance_widget(self, widget: tk.Widget, widget_type: str = "default"):
        """Enhance widget with accessibility features"""
        try:
            # Apply color scheme
            colors = self.get_color_scheme()
            widget.configure(bg=colors['bg'], fg=colors['text'])
            
            # Apply font size
            current_font = widget.cget('font')
            if isinstance(current_font, str):
                font_name = current_font
                font_size = self.base_font_sizes['normal']
            else:
                font_name = current_font[0]
                font_size = current_font[1] if len(current_font) > 1 else self.base_font_sizes['normal']
            
            new_font_size = self.get_font_size(font_size)
            widget.configure(font=(font_name, new_font_size))
            
            # Add focus indicator if enabled
            if self.focus_indicators:
                self.add_focus_indicator(widget)
            
            # Add keyboard navigation
            if self.keyboard_navigation:
                self.add_keyboard_navigation(widget)
            
            # Add tooltip if enabled
            if self.tooltips_enabled:
                self.add_tooltip(widget)
                
        except Exception:
            pass
    
    def add_focus_indicator(self, widget: tk.Widget):
        """Add focus indicator to widget"""
        def on_focus_in(event):
            colors = self.get_color_scheme()
            widget.configure(highlightbackground=colors['primary'], highlightthickness=2)
            self.announce_widget(widget, "focused")
        
        def on_focus_out(event):
            widget.configure(highlightthickness=0)
        
        widget.bind('<FocusIn>', on_focus_in)
        widget.bind('<FocusOut>', on_focus_out)
    
    def add_keyboard_navigation(self, widget: tk.Widget):
        """Add keyboard navigation to widget"""
        def on_key_press(event):
            if event.keysym == 'Tab':
                self.handle_tab_navigation(event)
            elif event.keysym == 'Return':
                self.handle_enter_key(widget, event)
            elif event.keysym == 'space':
                self.handle_space_key(widget, event)
        
        widget.bind('<KeyPress>', on_key_press)
        
        # Add to tab order
        if widget not in self.tab_order:
            self.tab_order.append(widget)
    
    def add_tooltip(self, widget: tk.Widget, tooltip_text: str = None):
        """Add tooltip to widget"""
        if not tooltip_text:
            # Generate tooltip from widget
            tooltip_text = self.generate_tooltip_text(widget)
        
        if tooltip_text:
            self.create_tooltip(widget, tooltip_text)
    
    def generate_tooltip_text(self, widget: tk.Widget) -> str:
        """Generate tooltip text for widget"""
        widget_class = widget.winfo_class()
        
        try:
            if widget_class == 'Button':
                text = widget.cget('text')
                return f"Button: {text}. Press Enter or Space to activate."
            elif widget_class == 'Entry':
                return "Text entry. Type to enter text."
            elif widget_class == 'Scale':
                return f"Slider. Current value: {widget.get()}. Use arrow keys to adjust."
            elif widget_class == 'Combobox':
                return f"Combo box. Current selection: {widget.get()}. Use arrow keys to navigate, Enter to select."
            elif widget_class == 'Checkbutton':
                var = widget.cget('variable')
                if var:
                    return f"Checkbox. Current state: {'checked' if var.get() else 'unchecked'}. Press Space to toggle."
            elif widget_class == 'Radiobutton':
                return "Radio button. Press Space to select."
            else:
                return f"{widget_class} widget"
        except Exception:
            return f"{widget_class} widget"
    
    def create_tooltip(self, widget: tk.Widget, text: str):
        """Create tooltip widget"""
        tooltip = None
        
        def on_enter(event):
            nonlocal tooltip
            if self.tooltips_enabled:
                x, y, _, _ = widget.bbox("insert")
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 25
                
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{x}+{y}")
                
                colors = self.get_color_scheme()
                label = tk.Label(tooltip, text=text, 
                               background=colors['card'],
                               foreground=colors['text'],
                               relief='solid', borderwidth=1,
                               font=('Segoe UI', self.get_font_size(9)))
                label.pack()
                
                self.speak(text)
        
        def on_leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def handle_tab_navigation(self, event):
        """Handle tab navigation"""
        if event.state & 0x0001:  # Shift key
            # Reverse tab
            self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_order)
        else:
            # Forward tab
            self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_order)
        
        if self.tab_order:
            next_widget = self.tab_order[self.current_tab_index]
            next_widget.focus_set()
            return "break"  # Prevent default tab behavior
    
    def handle_enter_key(self, widget: tk.Widget, event):
        """Handle Enter key"""
        widget_class = widget.winfo_class()
        
        if widget_class == 'Button':
            widget.invoke()
        elif widget_class == 'Checkbutton':
            widget.invoke()
        elif widget_class == 'Radiobutton':
            widget.invoke()
        elif widget_class == 'Combobox':
            # Show dropdown
            widget.event_generate('<Button-1>')
        
        return "break"
    
    def handle_space_key(self, widget: tk.Widget, event):
        """Handle Space key"""
        widget_class = widget.winfo_class()
        
        if widget_class in ['Button', 'Checkbutton', 'Radiobutton']:
            widget.invoke()
        
        return "break"
    
    def create_accessibility_panel(self, parent):
        """Create accessibility settings panel"""
        panel = tk.Frame(parent, bg=self.get_color_scheme()['bg'])
        
        # Title
        title = tk.Label(panel, text="Accessibility Settings",
                        font=('Segoe UI', self.get_font_size(14), 'bold'),
                        bg=self.get_color_scheme()['bg'],
                        fg=self.get_color_scheme()['text'])
        title.pack(pady=10)
        
        # High Contrast
        hc_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        hc_frame.pack(fill=tk.X, padx=20, pady=5)
        
        hc_var = tk.BooleanVar(value=self.high_contrast_mode)
        hc_cb = tk.Checkbutton(hc_frame, text="High Contrast Mode",
                               variable=hc_var,
                               command=lambda: self.set_high_contrast(hc_var.get()),
                               bg=self.get_color_scheme()['bg'],
                               fg=self.get_color_scheme()['text'])
        hc_cb.pack(side=tk.LEFT)
        
        # Screen Reader
        sr_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        sr_frame.pack(fill=tk.X, padx=20, pady=5)
        
        sr_var = tk.BooleanVar(value=self.screen_reader_enabled)
        sr_cb = tk.Checkbutton(sr_frame, text="Screen Reader",
                               variable=sr_var,
                               command=lambda: self.set_screen_reader(sr_var.get()),
                               bg=self.get_color_scheme()['bg'],
                               fg=self.get_color_scheme()['text'])
        sr_cb.pack(side=tk.LEFT)
        
        # Font Size
        fs_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        fs_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(fs_frame, text="Font Size:",
                bg=self.get_color_scheme()['bg'],
                fg=self.get_color_scheme()['text']).pack(side=tk.LEFT)
        
        fs_var = tk.DoubleVar(value=self.font_size_multiplier)
        fs_scale = tk.Scale(fs_frame, from_=0.5, to=3.0, resolution=0.1,
                           variable=fs_var, orient=tk.HORIZONTAL,
                           command=lambda v: self.set_font_size_multiplier(float(v)),
                           bg=self.get_color_scheme()['bg'],
                           fg=self.get_color_scheme()['text'])
        fs_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Color Blind Mode
        cb_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        cb_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(cb_frame, text="Color Blind Mode:",
                bg=self.get_color_scheme()['bg'],
                fg=self.get_color_scheme()['text']).pack(side=tk.LEFT)
        
        cb_var = tk.StringVar(value=self.color_blind_mode)
        cb_combo = ttk.Combobox(cb_frame, textvariable=cb_var,
                                values=['none', 'protanopia', 'deuteranopia', 'tritanopia'],
                                state='readonly')
        cb_combo.pack(side=tk.LEFT, padx=10)
        cb_combo.bind('<<ComboboxSelected>>', 
                     lambda e: self.set_color_blind_mode(cb_var.get()))
        
        # Keyboard Navigation
        kn_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        kn_frame.pack(fill=tk.X, padx=20, pady=5)
        
        kn_var = tk.BooleanVar(value=self.keyboard_navigation)
        kn_cb = tk.Checkbutton(kn_frame, text="Keyboard Navigation",
                               variable=kn_var,
                               command=lambda: self.save_settings({'keyboard_navigation': kn_var.get()}),
                               bg=self.get_color_scheme()['bg'],
                               fg=self.get_color_scheme()['text'])
        kn_cb.pack(side=tk.LEFT)
        
        # Focus Indicators
        fi_frame = tk.Frame(panel, bg=self.get_color_scheme()['bg'])
        fi_frame.pack(fill=tk.X, padx=20, pady=5)
        
        fi_var = tk.BooleanVar(value=self.settings.get('focus_indicators', True))
        fi_cb = tk.Checkbutton(fi_frame, text="Focus Indicators",
                               variable=fi_var,
                               command=lambda: self.save_settings({'focus_indicators': fi_var.get()}),
                               bg=self.get_color_scheme()['bg'],
                               fg=self.get_color_scheme()['text'])
        fi_cb.pack(side=tk.LEFT)
        
        # Test Button
        test_btn = tk.Button(panel, text="Test Accessibility",
                           command=self.test_accessibility,
                           bg=self.get_color_scheme()['primary'],
                           fg=self.get_color_scheme()['bg'])
        test_btn.pack(pady=20)
        
        return panel
    
    def test_accessibility(self):
        """Test accessibility features"""
        # Test screen reader
        if self.screen_reader_enabled:
            self.speak("Accessibility test started")
        
        # Create test dialog
        test_dialog = tk.Toplevel()
        test_dialog.title("Accessibility Test")
        test_dialog.geometry("400x300")
        
        # Apply accessibility enhancements
        colors = self.get_color_scheme()
        test_dialog.configure(bg=colors['bg'])
        
        # Test widgets
        tk.Label(test_dialog, text="Accessibility Test Dialog",
                font=('Segoe UI', self.get_font_size(12), 'bold'),
                bg=colors['bg'], fg=colors['text']).pack(pady=10)
        
        test_btn = tk.Button(test_dialog, text="Test Button",
                            command=lambda: self.speak("Button clicked"))
        test_btn.pack(pady=5)
        
        test_entry = tk.Entry(test_dialog)
        test_entry.pack(pady=5)
        
        test_scale = tk.Scale(test_dialog, from_=0, to=100, orient=tk.HORIZONTAL)
        test_scale.pack(pady=5)
        
        # Enhance all widgets
        for widget in test_dialog.winfo_children():
            self.enhance_widget(widget)
        
        # Announce dialog
        self.speak("Accessibility test dialog opened")
    
    @property
    def focus_indicators(self) -> bool:
        """Get focus indicators setting"""
        return self.settings.get('focus_indicators', True)
    
    @property
    def tooltips_enabled(self) -> bool:
        """Get tooltips enabled setting"""
        return self.settings.get('tooltips_enabled', True)
    
    @property
    def announcements_enabled(self) -> bool:
        """Get announcements enabled setting"""
        return self.settings.get('announcements_enabled', True)

# Global accessibility manager instance
accessibility = AccessibilityManager()

# Convenience functions
def enhance_widget(widget: tk.Widget, widget_type: str = "default"):
    """Enhance widget with accessibility features"""
    accessibility.enhance_widget(widget, widget_type)

def speak(text: str, interrupt: bool = False):
    """Speak text using screen reader"""
    accessibility.speak(text, interrupt)

def set_high_contrast(enabled: bool):
    """Set high contrast mode"""
    accessibility.set_high_contrast(enabled)

def set_color_blind_mode(mode: str):
    """Set color blind mode"""
    accessibility.set_color_blind_mode(mode)

def get_colors() -> Dict[str, str]:
    """Get current color scheme"""
    return accessibility.get_color_scheme()

def get_font_size(base_size: int) -> int:
    """Get adjusted font size"""
    return accessibility.get_font_size(base_size)

if __name__ == '__main__':
    # Test accessibility features
    print("Testing Accessibility Features")
    print(f"High contrast: {accessibility.high_contrast_mode}")
    print(f"Screen reader: {accessibility.screen_reader_enabled}")
    print(f"Font size multiplier: {accessibility.font_size_multiplier}")
    print(f"Color blind mode: {accessibility.color_blind_mode}")
    
    # Test color schemes
    colors = accessibility.get_colors()
    print(f"Current colors: {colors}")
    
    # Test screen reader
    if accessibility.screen_reader_enabled:
        accessibility.speak("Accessibility test started")
    
    # Test font size adjustment
    print(f"Normal font size: {accessibility.get_font_size(12)}")
    accessibility.set_font_size_multiplier(1.5)
    print(f"Large font size: {accessibility.get_font_size(12)}")
    
    # Test color blind modes
    for mode in ['none', 'protanopia', 'deuteranopia', 'tritanopia']:
        accessibility.set_color_blind_mode(mode)
        colors = accessibility.get_colors()
        print(f"Color blind mode {mode}: {colors['primary']}")
