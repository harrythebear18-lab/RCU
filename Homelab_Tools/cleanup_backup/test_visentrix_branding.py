#!/usr/bin/env python3
"""
Test Visentrix branding with PIL support
"""

import tkinter as tk
from tkinter import ttk
import os

# Try to import PIL
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("PIL/Pillow is available")
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow is NOT available")

def test_branding():
    """Test Visentrix branding display"""
    root = tk.Tk()
    root.title("Visentrix Branding Test")
    root.geometry("500x400")
    root.configure(bg='#1a1a1a')
    
    # Logo paths
    logo_paths = {
        'primary': 'D:\\Home Projects\\dx11(homelab)\\logo.png',
        'secondary': 'D:\\Home Projects\\dx11(homelab)\\logo1.png'
    }
    
    logo_images = {}
    
    print("Testing logo loading...")
    
    if PIL_AVAILABLE:
        # Try to load actual logos
        try:
            if os.path.exists(logo_paths['primary']):
                print(f"Loading primary logo: {logo_paths['primary']}")
                logo_img = Image.open(logo_paths['primary'])
                logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
                logo_images['primary'] = ImageTk.PhotoImage(logo_img)
                print("✓ Primary logo loaded")
            else:
                print(f"✗ Primary logo not found: {logo_paths['primary']}")
        except Exception as e:
            print(f"✗ Error loading primary logo: {e}")
        
        try:
            if os.path.exists(logo_paths['secondary']):
                print(f"Loading secondary logo: {logo_paths['secondary']}")
                logo_img = Image.open(logo_paths['secondary'])
                logo_img = logo_img.resize((48, 48), Image.Resampling.LANCZOS)
                logo_images['secondary'] = ImageTk.PhotoImage(logo_img)
                print("✓ Secondary logo loaded")
            else:
                print(f"✗ Secondary logo not found: {logo_paths['secondary']}")
        except Exception as e:
            print(f"✗ Error loading secondary logo: {e}")
    
    # Fallback to text-based branding
    if not logo_images:
        logo_images['primary'] = "⚡"
        logo_images['secondary'] = "◆"
        print("Using text-based branding fallback")
    
    # Create test interface
    header_frame = tk.Frame(root, bg='#1a1a1a', height=80)
    header_frame.pack(fill=tk.X, padx=20, pady=20)
    
    # Title section with logo
    title_section = tk.Frame(header_frame, bg='#1a1a1a')
    title_section.pack(side=tk.LEFT, anchor=tk.W, pady=20)
    
    # Title
    title_label = tk.Label(title_section, 
                          text="🏠 Homelab Tools - Complete System Management",
                          font=('Segoe UI', 18, 'bold'),
                          fg='#00ff88', 
                          bg='#1a1a1a')
    title_label.pack(side=tk.LEFT)
    
    # Add logo
    if isinstance(logo_images.get('primary'), str):
        # Text-based logo
        logo_label = tk.Label(title_section, text=logo_images['primary'], 
                            font=('Segoe UI', 24), 
                            fg='#00d4ff', bg='#1a1a1a')
        logo_label.pack(side=tk.LEFT, padx=(10, 0))
    else:
        # Image-based logo
        logo_label = tk.Label(title_section, image=logo_images['primary'], bg='#1a1a1a')
        logo_label.image = logo_images['primary']  # Keep reference
        logo_label.pack(side=tk.LEFT, padx=(10, 0))
    
    # Test cards
    cards_frame = tk.Frame(root, bg='#1a1a1a')
    cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create sample tool cards
    tools = ["CPU Monitor", "GPU Monitor", "Network Monitor"]
    for i, tool_name in enumerate(tools):
        card = tk.Frame(cards_frame, bg='#2d2d2d', relief='raised', bd=1)
        card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
        cards_frame.grid_columnconfigure(i, weight=1)
        
        # Tool icon/logo
        if i == 0 and isinstance(logo_images.get('secondary'), str):
            # Show text logo on first card
            icon_label = tk.Label(card, text=logo_images['secondary'], 
                                font=('Segoe UI', 20), 
                                fg='#00d4ff', bg='#2d2d2d')
            icon_label.pack(pady=(15, 5))
        elif i == 0 and 'secondary' in logo_images:
            # Show image logo on first card
            icon_label = tk.Label(card, image=logo_images['secondary'], bg='#2d2d2d')
            icon_label.image = logo_images['secondary']
            icon_label.pack(pady=(15, 5))
        else:
            # Show regular icon
            icon_label = tk.Label(card, text="🖥️", 
                                font=('Segoe UI', 24), 
                                fg='#00ff88', bg='#2d2d2d')
            icon_label.pack(pady=(15, 5))
        
        # Tool name
        name_label = tk.Label(card, text=tool_name, 
                            font=('Segoe UI', 10, 'bold'), 
                            fg='white', bg='#2d2d2d')
        name_label.pack(pady=(0, 5))
        
        # Launch button
        launch_btn = tk.Button(card, text="🚀 Launch", 
                             bg='#00ff88', fg='#1a1a1a',
                             font=('Segoe UI', 9, 'bold'), relief='flat', bd=0)
        launch_btn.pack(pady=(10, 15))
    
    # Status
    status_text = f"PIL Available: {PIL_AVAILABLE} | Logos Loaded: {len([k for k, v in logo_images.items() if not isinstance(v, str)])}"
    status_label = tk.Label(root, text=status_text, 
                          bg='#2d2d2d', fg='#b0b0b0', 
                          font=('Segoe UI', 9))
    status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
    
    print(f"Test ready - PIL: {PIL_AVAILABLE}, Logos: {len(logo_images)}")
    root.mainloop()

if __name__ == "__main__":
    test_branding()
