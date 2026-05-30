#!/usr/bin/env python3
"""
PC Authentication GUI
Simple GUI for managing PC-to-PC authentication in the same subnet.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from pathlib import Path
import json

# Import PC auth system
from pc_auth_system import pc_auth_system, AuthStatus, PeerRole

class PCAuthGUI:
    """GUI for PC authentication management"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 PC-to-PC Authentication")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
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
        }
        
        # GUI state
        self.selected_peer = None
        self.refresh_active = False
        self.refresh_thread = None
        
        # Create UI
        self.create_ui()
        
        # Start GUI monitoring
        self.start_gui_monitoring()
    
    def create_ui(self):
        """Create the GUI interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create main sections
        self.create_system_info(content_frame)
        self.create_peer_management(content_frame)
        self.create_auth_events(content_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title and status
        title_frame = tk.Frame(header_frame, bg=self.colors['card'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        title_label = tk.Label(title_frame, text="🔐 PC-to-PC Authentication",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        self.local_info_label = tk.Label(title_frame, text=f"Local: {pc_auth_system.local_peer.name} ({pc_auth_system.local_peer.ip_address})",
                                         font=('Segoe UI', 10),
                                         fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.local_info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg=self.colors['card'])
        control_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.discovery_btn = tk.Button(control_frame, text="🔍 Discover",
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['primary'], fg=self.colors['bg'],
                                      relief='flat', cursor='hand2',
                                      command=self.toggle_discovery)
        self.discovery_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=self.colors['success'], fg=self.colors['bg'],
                                    relief='flat', cursor='hand2',
                                    command=self.refresh_display)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = tk.Button(control_frame, text="⚙️ Settings",
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['warning'], fg=self.colors['bg'],
                                     relief='flat', cursor='hand2',
                                     command=self.open_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
    
    def create_system_info(self, parent):
        """Create system information section"""
        info_frame = tk.Frame(parent, bg=self.colors['card'])
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(info_frame, text="📊 System Information",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Info cards container
        cards_container = tk.Frame(info_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Create info cards
        self.create_info_card(cards_container, "Total Peers", "total_peers", 0)
        self.create_info_card(cards_container, "Trusted", "trusted_peers", 1)
        self.create_info_card(cards_container, "Blocked", "blocked_peers", 2)
        self.create_info_card(cards_container, "Active Sessions", "active_sessions", 3)
    
    def create_info_card(self, parent, title, card_type, column):
        """Create individual info card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text=title,
                              font=('Segoe UI', 11, 'bold'),
                              fg=self.colors['text_secondary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        # Value
        value_label = tk.Label(content_frame, text="0",
                              font=('Segoe UI', 20, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        value_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Store references
        setattr(self, f"{card_type}_value", value_label)
    
    def create_peer_management(self, parent):
        """Create peer management section"""
        peer_frame = tk.Frame(parent, bg=self.colors['card'])
        peer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title
        title_label = tk.Label(peer_frame, text="👥 Peer Management",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Create paned window for peer list and details
        paned = ttk.PanedWindow(peer_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Peer list
        list_frame = tk.Frame(paned, bg=self.colors['card'])
        paned.add(list_frame, weight=1)
        
        self.create_peer_list(list_frame)
        
        # Peer details
        details_frame = tk.Frame(paned, bg=self.colors['card'])
        paned.add(details_frame, weight=1)
        
        self.create_peer_details(details_frame)
    
    def create_peer_list(self, parent):
        """Create peer list"""
        # List header
        header_frame = tk.Frame(parent, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(header_frame, text="Discovered Peers",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Peer listbox
        list_frame = tk.Frame(parent, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for peers
        columns = ('Name', 'IP Address', 'Role', 'Status', 'Last Seen')
        self.peers_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.peers_tree.heading(col, text=col)
            self.peers_tree.column(col, width=100)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        self.peers_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.peers_tree.bind('<<TreeviewSelect>>', self.on_peer_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.peers_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.peers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(parent, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.trust_btn = tk.Button(button_frame, text="✅ Trust",
                                  font=('Segoe UI', 9),
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.trust_selected_peer)
        self.trust_btn.pack(side=tk.LEFT, padx=5)
        
        self.block_btn = tk.Button(button_frame, text="🚫 Block",
                                   font=('Segoe UI', 9),
                                   bg=self.colors['danger'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2',
                                   command=self.block_selected_peer)
        self.block_btn.pack(side=tk.LEFT, padx=5)
        
        self.auth_btn = tk.Button(button_frame, text="🔐 Authenticate",
                                  font=('Segoe UI', 9),
                                  bg=self.colors['primary'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.authenticate_selected_peer)
        self.auth_btn.pack(side=tk.LEFT, padx=5)
    
    def create_peer_details(self, parent):
        """Create peer details panel"""
        # Details header
        header_frame = tk.Frame(parent, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(header_frame, text="Peer Details",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Details content
        details_frame = tk.Frame(parent, bg=self.colors['card'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Details text
        self.details_text = scrolledtext.ScrolledText(
            details_frame, height=15, width=50,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = tk.Frame(parent, bg=self.colors['card'])
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.connect_btn = tk.Button(action_frame, text="🔗 Connect",
                                     font=('Segoe UI', 9),
                                     bg=self.colors['primary'], fg=self.colors['bg'],
                                     relief='flat', cursor='hand2',
                                     command=self.connect_to_peer)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = tk.Button(action_frame, text="🗑️ Remove",
                                    font=('Segoe UI', 9),
                                    bg=self.colors['warning'], fg=self.colors['bg'],
                                    relief='flat', cursor='hand2',
                                    command=self.remove_selected_peer)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
    
    def create_auth_events(self, parent):
        """Create authentication events section"""
        events_frame = tk.Frame(parent, bg=self.colors['card'])
        events_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(events_frame, text="📋 Authentication Events",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Events container
        events_container = tk.Frame(events_frame, bg=self.colors['card'])
        events_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Events text
        self.events_text = scrolledtext.ScrolledText(
            events_container, height=8, width=120,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.events_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = tk.Frame(events_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.clear_events_btn = tk.Button(button_frame, text="🗑️ Clear Events",
                                          font=('Segoe UI', 9),
                                          bg=self.colors['warning'], fg=self.colors['bg'],
                                          relief='flat', cursor='hand2',
                                          command=self.clear_events)
        self.clear_events_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_events_btn = tk.Button(button_frame, text="📥 Export Events",
                                            font=('Segoe UI', 9),
                                            bg=self.colors['primary'], fg=self.colors['bg'],
                                            relief='flat', cursor='hand2',
                                            command=self.export_events)
        self.export_events_btn.pack(side=tk.LEFT, padx=5)
    
    def toggle_discovery(self):
        """Toggle network discovery"""
        try:
            if pc_auth_system.discovery_active:
                pc_auth_system.stop_discovery_service()
                self.discovery_btn.config(text="🔍 Discover", bg=self.colors['primary'])
                messagebox.showinfo("Discovery", "Network discovery stopped")
            else:
                pc_auth_system.start_discovery_service()
                self.discovery_btn.config(text="⏹️ Stop", bg=self.colors['danger'])
                messagebox.showinfo("Discovery", "Network discovery started")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle discovery: {e}")
    
    def refresh_display(self):
        """Refresh the display"""
        try:
            # Update system info cards
            self.update_system_info()
            
            # Update peer list
            self.update_peer_list()
            
            # Update events
            self.update_events()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {e}")
    
    def update_system_info(self):
        """Update system information cards"""
        try:
            status = pc_auth_system.get_system_status()
            
            # Update info cards
            peers = status.get('peers', {})
            self.total_peers_value.config(text=str(peers.get('total', 0)))
            self.trusted_peers_value.config(text=str(peers.get('trusted', 0)))
            self.blocked_peers_value.config(text=str(peers.get('blocked', 0)))
            
            sessions = status.get('sessions', {})
            self.active_sessions_value.config(text=str(sessions.get('active', 0)))
            
        except Exception as e:
            print(f"Error updating system info: {e}")
    
    def update_peer_list(self):
        """Update peer list"""
        try:
            # Clear existing items
            for item in self.peers_tree.get_children():
                self.peers_tree.delete(item)
            
            # Add peers to tree
            for peer_id, peer in pc_auth_system.peers.items():
                # Skip local peer
                if peer_id == pc_auth_system.local_peer.id:
                    continue
                
                last_seen = peer.last_seen.strftime('%H:%M:%S') if peer.last_seen else 'Never'
                
                # Determine status color
                status_text = peer.status.value
                if peer_id in pc_auth_system.trusted_peers:
                    status_text += " (Trusted)"
                elif peer_id in pc_auth_system.blocked_peers:
                    status_text += " (Blocked)"
                
                self.peers_tree.insert('', 'end', values=(
                    peer.name,
                    peer.ip_address,
                    peer.role.value,
                    status_text,
                    last_seen
                ), tags=(peer_id,))
                
        except Exception as e:
            print(f"Error updating peer list: {e}")
    
    def update_events(self):
        """Update authentication events"""
        try:
            # Clear existing events
            self.events_text.delete(1.0, tk.END)
            
            # Add recent events
            events = [
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 PC Authentication System Active\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Total Peers: {len(pc_auth_system.peers)}\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Discovery: {'Active' if pc_auth_system.discovery_active else 'Inactive'}\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔐 Active Sessions: {len(pc_auth_system.session_tokens)}\n"
            ]
            
            for event in events:
                self.events_text.insert(tk.END, event)
            
            self.events_text.see(tk.END)
            
        except Exception as e:
            print(f"Error updating events: {e}")
    
    def on_peer_select(self, event):
        """Handle peer selection"""
        try:
            selection = self.peers_tree.selection()
            if not selection:
                self.selected_peer = None
                return
            
            # Get peer ID from selection
            item = self.peers_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2:
                # Find peer by IP address
                ip_address = values[1]
                for peer_id, peer in pc_auth_system.peers.items():
                    if peer.ip_address == ip_address:
                        self.selected_peer = peer_id
                        self.update_peer_details()
                        break
                        
        except Exception as e:
            print(f"Error handling peer selection: {e}")
    
    def update_peer_details(self):
        """Update peer details panel"""
        try:
            if not self.selected_peer:
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, "No peer selected")
                return
            
            peer_status = pc_auth_system.get_peer_status(self.selected_peer)
            
            # Format peer details
            details = f"""Peer Information:
================
ID: {peer_status.get('id', 'N/A')}
Name: {peer_status.get('name', 'N/A')}
Hostname: {peer_status.get('hostname', 'N/A')}
IP Address: {peer_status.get('ip_address', 'N/A')}
Role: {peer_status.get('role', 'N/A')}
Status: {peer_status.get('status', 'N/A')}
Fingerprint: {peer_status.get('fingerprint', 'N/A')}

Trust Information:
==================
Trusted: {peer_status.get('is_trusted', False)}
Blocked: {peer_status.get('is_blocked', False)}
Has Session: {peer_status.get('has_session', False)}

Timestamps:
===========
Created: {peer_status.get('created_at', 'N/A')}
Last Seen: {peer_status.get('last_seen', 'N/A')}
"""
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, details)
            
        except Exception as e:
            print(f"Error updating peer details: {e}")
    
    def trust_selected_peer(self):
        """Trust selected peer"""
        try:
            if not self.selected_peer:
                messagebox.showwarning("Warning", "Please select a peer to trust")
                return
            
            if messagebox.askyesno("Trust Peer", f"Trust selected peer? This will allow automatic authentication."):
                if pc_auth_system.trust_peer(self.selected_peer):
                    messagebox.showinfo("Success", "Peer trusted successfully!")
                    self.refresh_display()
                else:
                    messagebox.showerror("Error", "Failed to trust peer")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to trust peer: {e}")
    
    def block_selected_peer(self):
        """Block selected peer"""
        try:
            if not self.selected_peer:
                messagebox.showwarning("Warning", "Please select a peer to block")
                return
            
            if messagebox.askyesno("Block Peer", f"Block selected peer? This will prevent all authentication attempts."):
                if pc_auth_system.block_peer(self.selected_peer):
                    messagebox.showinfo("Success", "Peer blocked successfully!")
                    self.refresh_display()
                else:
                    messagebox.showerror("Error", "Failed to block peer")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to block peer: {e}")
    
    def authenticate_selected_peer(self):
        """Authenticate with selected peer"""
        try:
            if not self.selected_peer:
                messagebox.showwarning("Warning", "Please select a peer to authenticate with")
                return
            
            # Create authentication dialog
            self.create_auth_dialog()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to authenticate: {e}")
    
    def create_auth_dialog(self):
        """Create authentication dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Authenticate with Peer")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['card'])
        
        # Peer info
        peer = pc_auth_system.peers.get(self.selected_peer)
        if peer:
            tk.Label(dialog, text=f"Authenticating with: {peer.name}",
                    bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        # Authentication method
        tk.Label(dialog, text="Authentication Method:",
                bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        method_var = tk.StringVar(value="fingerprint")
        methods = ["fingerprint", "password", "certificate"]
        
        for method in methods:
            tk.Radiobutton(dialog, text=method.capitalize(),
                          variable=method_var, value=method,
                          bg=self.colors['card'], fg=self.colors['text'],
                          selectcolor=self.colors['bg']).pack(pady=5)
        
        # Credentials
        tk.Label(dialog, text="Credentials:",
                bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        credentials_var = tk.StringVar()
        credentials_entry = tk.Entry(dialog, textvariable=credentials_var, 
                                   bg=self.colors['bg'], fg=self.colors['text'])
        credentials_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Authenticate", bg=self.colors['primary'], fg=self.colors['bg'],
                 command=lambda: self.perform_authentication(method_var.get(), credentials_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def perform_authentication(self, method: str, credentials: str, dialog):
        """Perform authentication with peer"""
        try:
            # Create credentials dictionary
            auth_credentials = {
                'method': method,
                'fingerprint': pc_auth_system.local_peer.fingerprint,
                'timestamp': datetime.now().isoformat()
            }
            
            if method == "password":
                auth_credentials['password'] = credentials
            elif method == "certificate":
                auth_credentials['certificate'] = credentials
            
            # Authenticate (simplified version)
            session_token = pc_auth_system.authenticate_peer(self.selected_peer, auth_credentials)
            
            if session_token:
                messagebox.showinfo("Success", f"Authentication successful!\nSession Token: {session_token}")
                dialog.destroy()
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Authentication failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")
    
    def connect_to_peer(self):
        """Connect to selected peer"""
        try:
            if not self.selected_peer:
                messagebox.showwarning("Warning", "Please select a peer to connect to")
                return
            
            peer = pc_auth_system.peers.get(self.selected_peer)
            if peer:
                messagebox.showinfo("Connect", f"Connection to {peer.name} ({peer.ip_address}) would be established here")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")
    
    def remove_selected_peer(self):
        """Remove selected peer"""
        try:
            if not self.selected_peer:
                messagebox.showwarning("Warning", "Please select a peer to remove")
                return
            
            if messagebox.askyesno("Remove Peer", f"Remove selected peer from the system?"):
                # Remove from memory (simplified version)
                if self.selected_peer in pc_auth_system.peers:
                    del pc_auth_system.peers[self.selected_peer]
                
                messagebox.showinfo("Success", "Peer removed successfully!")
                self.selected_peer = None
                self.refresh_display()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove peer: {e}")
    
    def clear_events(self):
        """Clear events display"""
        try:
            self.events_text.delete(1.0, tk.END)
            self.events_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Events cleared\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear events: {e}")
    
    def export_events(self):
        """Export events to file"""
        try:
            events_content = self.events_text.get(1.0, tk.END)
            
            # Save to file
            events_file = Path(__file__).parent / f"auth_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(events_file, 'w') as f:
                f.write(events_content)
            
            messagebox.showinfo("Export", f"Events exported to {events_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export events: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            # Create settings dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Authentication Settings")
            dialog.geometry("500x400")
            dialog.configure(bg=self.colors['card'])
            
            # Settings title
            tk.Label(dialog, text="Authentication System Settings",
                    font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
            
            # Settings content
            settings_content = f"""
Current Settings:
================
Subnet: {pc_auth_system.settings.get('subnet', '192.168.1.0/24')}
Discovery Enabled: {pc_auth_system.settings.get('discovery_enabled', True)}
Discovery Interval: {pc_auth_system.settings.get('discovery_interval', 30)}s
Auth Timeout: {pc_auth_system.settings.get('auth_timeout', 3600)}s
Session Timeout: {pc_auth_system.settings.get('session_timeout', 1800)}s
Max Peers: {pc_auth_system.settings.get('max_peers', 20)}
Auto Trust: {pc_auth_system.settings.get('auto_trust', False)}
Require Approval: {pc_auth_system.settings.get('require_approval', True)}
Encryption Enabled: {pc_auth_system.settings.get('encryption_enabled', True)}
"""
            
            settings_text = scrolledtext.ScrolledText(
                dialog, height=15, width=60,
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Consolas', 9), relief='flat'
            )
            settings_text.pack(padx=10, pady=10)
            settings_text.insert(tk.END, settings_content)
            settings_text.config(state='disabled')
            
            # Close button
            tk.Button(dialog, text="Close", bg=self.colors['primary'], fg=self.colors['bg'],
                     command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def start_gui_monitoring(self):
        """Start GUI monitoring"""
        self.refresh_active = True
        self.refresh_thread = threading.Thread(target=self._gui_monitoring_loop, daemon=True)
        self.refresh_thread.start()
    
    def _gui_monitoring_loop(self):
        """GUI monitoring loop"""
        while self.refresh_active:
            try:
                self.refresh_display()
                time.sleep(30)  # Refresh every 30 seconds
            except Exception as e:
                print(f"GUI monitoring error: {e}")
                time.sleep(10)

if __name__ == '__main__':
    # Create GUI window
    root = tk.Tk()
    gui = PCAuthGUI(root)
    
    # Handle window closing
    def on_closing():
        try:
            pc_auth_system.stop_discovery_service()
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()
