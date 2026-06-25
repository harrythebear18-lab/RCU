#!/usr/bin/env python3
"""
Unified Dark Theme Configuration for Homelab Tools
Consistent modern dark theme across all Homelab tools
"""

class HomelabTheme:
    """Unified dark theme configuration for all Homelab tools"""
    
    # Color palette
    COLORS = {
        # Background colors
        'bg_primary': '#1a1a1a',      # Main background
        'bg_secondary': '#2d2d2d',    # Card/panel background
        'bg_tertiary': '#3a3a3a',     # Hover/active states
        'bg_accent': '#242424',       # Graph/chart backgrounds
        
        # Text colors
        'text_primary': '#ffffff',     # Main text
        'text_secondary': '#b0b0b0',  # Secondary text
        'text_muted': '#808080',      # Muted/disabled text
        
        # Status colors
        'primary': '#00d4ff',         # Primary accent (cyan)
        'success': '#00ff88',         # Success (green)
        'warning': '#ffaa00',         # Warning (orange)
        'danger': '#ff4444',          # Danger (red)
        'info': '#0078ff',            # Info (blue)
        
        # Border colors
        'border': '#404040',          # Standard border
        'border_light': '#555555',    # Light border
        'border_dark': '#333333',     # Dark border
        
        # Graph colors
        'graph_bg': '#242424',        # Graph background
        'grid': '#404040',            # Grid lines
        'line_primary': '#00d4ff',    # Primary line
        'line_secondary': '#00ff88',  # Secondary line
        'line_tertiary': '#ffaa00'    # Tertiary line
    }
    
    # Typography
    FONTS = {
        'primary': ('Segoe UI', 10),
        'primary_bold': ('Segoe UI', 10, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'title': ('Segoe UI', 16, 'bold'),
        'subtitle': ('Segoe UI', 14, 'bold'),
        'mono': ('Consolas', 10),
        'mono_bold': ('Consolas', 10, 'bold'),
        'small': ('Segoe UI', 9),
        'large': ('Segoe UI', 11)
    }
    
    # Spacing and sizing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24
    }
    
    # Border radius
    BORDER_RADIUS = {
        'small': 4,
        'medium': 6,
        'large': 8
    }
    
    # Shadow effects
    SHADOWS = {
        'light': '#00000020',
        'medium': '#00000040',
        'dark': '#00000060'
    }
    
    @classmethod
    def get_style_config(cls):
        """Get complete style configuration for ttk.Style"""
        return {
            # Frame styles
            'TFrame': {
                'background': cls.COLORS['bg_primary']
            },
            'Card.TFrame': {
                'background': cls.COLORS['bg_secondary'],
                'relief': 'flat',
                'borderwidth': 1
            },
            'Panel.TFrame': {
                'background': cls.COLORS['bg_tertiary'],
                'relief': 'flat',
                'borderwidth': 1
            },
            
            # Label styles
            'Title.TLabel': {
                'background': cls.COLORS['bg_primary'],
                'foreground': cls.COLORS['primary'],
                'font': cls.FONTS['title']
            },
            'Subtitle.TLabel': {
                'background': cls.COLORS['bg_primary'],
                'foreground': cls.COLORS['text_primary'],
                'font': cls.FONTS['subtitle']
            },
            'Heading.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['text_primary'],
                'font': cls.FONTS['heading']
            },
            'Info.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['text_primary'],
                'font': cls.FONTS['primary']
            },
            'InfoValue.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['primary'],
                'font': cls.FONTS['primary_bold']
            },
            'Secondary.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['text_secondary'],
                'font': cls.FONTS['primary']
            },
            'Muted.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['text_muted'],
                'font': cls.FONTS['small']
            },
            'Success.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['success'],
                'font': cls.FONTS['primary_bold']
            },
            'Warning.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['warning'],
                'font': cls.FONTS['primary_bold']
            },
            'Danger.TLabel': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['danger'],
                'font': cls.FONTS['primary_bold']
            },
            
            # Button styles
            'Primary.TButton': {
                'background': cls.COLORS['primary'],
                'foreground': cls.COLORS['bg_primary'],
                'font': cls.FONTS['primary_bold'],
                'relief': 'flat',
                'borderwidth': 0,
                'focuscolor': 'none'
            },
            'Success.TButton': {
                'background': cls.COLORS['success'],
                'foreground': cls.COLORS['bg_primary'],
                'font': cls.FONTS['primary_bold'],
                'relief': 'flat',
                'borderwidth': 0,
                'focuscolor': 'none'
            },
            'Warning.TButton': {
                'background': cls.COLORS['warning'],
                'foreground': cls.COLORS['bg_primary'],
                'font': cls.FONTS['primary_bold'],
                'relief': 'flat',
                'borderwidth': 0,
                'focuscolor': 'none'
            },
            'Danger.TButton': {
                'background': cls.COLORS['danger'],
                'foreground': cls.COLORS['bg_primary'],
                'font': cls.FONTS['primary_bold'],
                'relief': 'flat',
                'borderwidth': 0,
                'focuscolor': 'none'
            },
            'Secondary.TButton': {
                'background': cls.COLORS['bg_tertiary'],
                'foreground': cls.COLORS['text_primary'],
                'font': cls.FONTS['primary'],
                'relief': 'flat',
                'borderwidth': 1,
                'focuscolor': 'none'
            },
            
            # Entry styles
            'TEntry': {
                'background': cls.COLORS['bg_tertiary'],
                'foreground': cls.COLORS['text_primary'],
                'borderwidth': 1,
                'relief': 'solid',
                'insertcolor': cls.COLORS['primary'],
                'selectbackground': cls.COLORS['primary'],
                'selectforeground': cls.COLORS['bg_primary']
            },
            
            # Progress bar styles
            'Modern.Horizontal.TProgressbar': {
                'background': cls.COLORS['primary'],
                'troughcolor': cls.COLORS['bg_tertiary'],
                'borderwidth': 0,
                'lightcolor': cls.COLORS['primary'],
                'darkcolor': cls.COLORS['primary']
            },
            'Success.Horizontal.TProgressbar': {
                'background': cls.COLORS['success'],
                'troughcolor': cls.COLORS['bg_tertiary'],
                'borderwidth': 0
            },
            'Warning.Horizontal.TProgressbar': {
                'background': cls.COLORS['warning'],
                'troughcolor': cls.COLORS['bg_tertiary'],
                'borderwidth': 0
            },
            'Danger.Horizontal.TProgressbar': {
                'background': cls.COLORS['danger'],
                'troughcolor': cls.COLORS['bg_tertiary'],
                'borderwidth': 0
            },
            
            # Notebook (tab) styles
            'TNotebook': {
                'background': cls.COLORS['bg_primary'],
                'borderwidth': 0
            },
            'TNotebook.Tab': {
                'background': cls.COLORS['bg_secondary'],
                'foreground': cls.COLORS['text_secondary'],
                'padding': [cls.SPACING['md'], cls.SPACING['sm']],
                'font': cls.FONTS['primary']
            },
            'TNotebook.Tab': {
                'background': cls.COLORS['bg_tertiary'],
                'foreground': cls.COLORS['text_primary'],
                'padding': [cls.SPACING['md'], cls.SPACING['sm']],
                'font': cls.FONTS['primary_bold']
            }
        }
    
    @classmethod
    def apply_styles(cls, style):
        """Apply theme styles to ttk.Style instance"""
        style.theme_use('clam')
        
        config = cls.get_style_config()
        for style_name, style_config in config.items():
            style.configure(style_name, **style_config)
        
        # Configure map for hover states
        style.map('Primary.TButton',
                 background=[('active', cls.COLORS['bg_tertiary']),
                           ('disabled', cls.COLORS['bg_tertiary'])])
        style.map('Success.TButton',
                 background=[('active', cls.COLORS['bg_tertiary']),
                           ('disabled', cls.COLORS['bg_tertiary'])])
        style.map('Warning.TButton',
                 background=[('active', cls.COLORS['bg_tertiary']),
                           ('disabled', cls.COLORS['bg_tertiary'])])
        style.map('Danger.TButton',
                 background=[('active', cls.COLORS['bg_tertiary']),
                           ('disabled', cls.COLORS['bg_tertiary'])])
        style.map('Secondary.TButton',
                 background=[('active', cls.COLORS['bg_secondary']),
                           ('disabled', cls.COLORS['bg_tertiary'])])
        
        return style
    
    @classmethod
    def get_matplotlib_colors(cls):
        """Get matplotlib color configuration"""
        return {
            'figure.facecolor': cls.COLORS['bg_primary'],
            'axes.facecolor': cls.COLORS['graph_bg'],
            'axes.edgecolor': cls.COLORS['border'],
            'axes.labelcolor': cls.COLORS['text_primary'],
            'axes.titlesize': 14,
            'axes.labelsize': 10,
            'xtick.color': cls.COLORS['text_secondary'],
            'ytick.color': cls.COLORS['text_secondary'],
            'grid.color': cls.COLORS['grid'],
            'grid.linestyle': '--',
            'grid.alpha': 0.3,
            'text.color': cls.COLORS['text_primary'],
            'font.family': 'Segoe UI',
            'font.size': 10
        }
    
    @classmethod
    def configure_matplotlib(cls):
        """Configure matplotlib with dark theme"""
        try:
            import matplotlib.pyplot as plt
            colors = cls.get_matplotlib_colors()
            
            # Apply all matplotlib settings
            for key, value in colors.items():
                plt.rcParams[key] = value
            
            # Set color cycle
            plt.rcParams['axes.prop_cycle'] = plt.cycler(
                'color', [
                    cls.COLORS['line_primary'],
                    cls.COLORS['line_secondary'],
                    cls.COLORS['line_tertiary'],
                    cls.COLORS['info'],
                    cls.COLORS['warning']
                ]
            )
            
            return True
        except ImportError:
            return False
