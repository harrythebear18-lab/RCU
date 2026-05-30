#!/usr/bin/env python3
"""
Test script to verify Visentrix logo loading
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

def test_logo_loading():
    """Test if Visentrix logos can be loaded"""
    root = tk.Tk()
    root.title("Logo Test")
    root.geometry("400x300")
    root.configure(bg='#1a1a1a')
    
    # Logo paths
    logo_paths = {
        'primary': 'D:\\Home Projects\\dx11(homelab)\\logo.png',
        'secondary': 'D:\\Home Projects\\dx11(homelab)\\logo1.png'
    }
    
    logo_images = {}
    
    print("Testing logo loading...")
    
    # Load primary logo
    try:
        if os.path.exists(logo_paths['primary']):
            print(f"Primary logo found: {logo_paths['primary']}")
            logo_img = Image.open(logo_paths['primary'])
            logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
            logo_images['primary'] = ImageTk.PhotoImage(logo_img)
            print("Primary logo loaded successfully!")
        else:
            print(f"Primary logo not found: {logo_paths['primary']}")
    except Exception as e:
        print(f"Error loading primary logo: {e}")
    
    # Load secondary logo
    try:
        if os.path.exists(logo_paths['secondary']):
            print(f"Secondary logo found: {logo_paths['secondary']}")
            logo_img = Image.open(logo_paths['secondary'])
            logo_img = logo_img.resize((48, 48), Image.Resampling.LANCZOS)
            logo_images['secondary'] = ImageTk.PhotoImage(logo_img)
            print("Secondary logo loaded successfully!")
        else:
            print(f"Secondary logo not found: {logo_paths['secondary']}")
    except Exception as e:
        print(f"Error loading secondary logo: {e}")
    
    # Display logos
    if 'primary' in logo_images:
        label1 = tk.Label(root, image=logo_images['primary'], bg='#1a1a1a')
        label1.image = logo_images['primary']
        label1.pack(pady=10)
        tk.Label(root, text="Primary Logo", bg='#1a1a1a', fg='white').pack()
    
    if 'secondary' in logo_images:
        label2 = tk.Label(root, image=logo_images['secondary'], bg='#1a1a1a')
        label2.image = logo_images['secondary']
        label2.pack(pady=10)
        tk.Label(root, text="Secondary Logo", bg='#1a1a1a', fg='white').pack()
    
    if not logo_images:
        tk.Label(root, text="No logos loaded!", bg='#1a1a1a', fg='red', font=('Arial', 14, 'bold')).pack(pady=50)
    
    print(f"Loaded {len(logo_images)} logos")
    root.mainloop()

if __name__ == "__main__":
    test_logo_loading()
