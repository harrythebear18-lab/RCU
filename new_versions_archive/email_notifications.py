#!/usr/bin/env python3
"""
Email Notifications System
Handles email alerts and notifications for system monitoring.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import queue
import time

class EmailNotificationManager:
    """Manages email notifications and alerts"""
    
    def __init__(self, settings_file="email_settings.json"):
        self.settings_file = os.path.join(os.path.dirname(__file__), settings_file)
        self.notification_queue = queue.Queue()
        self.email_thread = None
        self.running = False
        
        # Default email settings
        self.default_settings = {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "to_emails": [],
            "use_tls": True,
            "use_ssl": False,
            "notification_types": {
                "critical_alerts": True,
                "warning_alerts": False,
                "daily_reports": False,
                "weekly_reports": True,
                "system_health": False,
                "backup_complete": True,
                "optimization_complete": False
            },
            "scheduling": {
                "daily_report_time": "09:00",
                "weekly_report_day": "monday",
                "weekly_report_time": "09:00"
            },
            "templates": {
                "alert_subject": "🚨 System Alert: {alert_type}",
                "report_subject": "📊 System Report: {report_type}",
                "backup_subject": "💾 Backup Complete: {backup_name}"
            }
        }
        
        # Load settings
        self.settings = self.load_settings()
        
        # Start email thread if enabled
        if self.settings["enabled"]:
            self.start_email_service()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load email settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            else:
                # Create default settings file
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading email settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save email settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving email settings: {e}")
            return False
    
    def start_email_service(self):
        """Start email notification service"""
        if not self.running and self.settings["enabled"]:
            self.running = True
            self.email_thread = threading.Thread(target=self._email_worker, daemon=True)
            self.email_thread.start()
    
    def stop_email_service(self):
        """Stop email notification service"""
        self.running = False
        if self.email_thread:
            self.email_thread.join(timeout=5)
    
    def send_alert_notification(self, alert_type: str, message: str, severity: str, 
                              details: Optional[Dict[str, Any]] = None) -> bool:
        """Send alert notification"""
        if not self.settings["enabled"]:
            return False
        
        # Check if this alert type is enabled
        if severity == "critical" and not self.settings["notification_types"]["critical_alerts"]:
            return False
        elif severity == "warning" and not self.settings["notification_types"]["warning_alerts"]:
            return False
        
        notification = {
            "type": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.notification_queue.put(notification)
        return True
    
    def send_report_notification(self, report_type: str, report_data: Dict[str, Any], 
                               attachments: Optional[List[str]] = None) -> bool:
        """Send report notification"""
        if not self.settings["enabled"]:
            return False
        
        # Check if this report type is enabled
        if report_type == "daily" and not self.settings["notification_types"]["daily_reports"]:
            return False
        elif report_type == "weekly" and not self.settings["notification_types"]["weekly_reports"]:
            return False
        
        notification = {
            "type": "report",
            "report_type": report_type,
            "report_data": report_data,
            "attachments": attachments or [],
            "timestamp": datetime.now().isoformat()
        }
        
        self.notification_queue.put(notification)
        return True
    
    def send_backup_notification(self, backup_name: str, backup_info: Dict[str, Any]) -> bool:
        """Send backup completion notification"""
        if not self.settings["enabled"]:
            return False
        
        if not self.settings["notification_types"]["backup_complete"]:
            return False
        
        notification = {
            "type": "backup",
            "backup_name": backup_name,
            "backup_info": backup_info,
            "timestamp": datetime.now().isoformat()
        }
        
        self.notification_queue.put(notification)
        return True
    
    def send_system_health_notification(self, health_score: Dict[str, Any]) -> bool:
        """Send system health notification"""
        if not self.settings["enabled"]:
            return False
        
        if not self.settings["notification_types"]["system_health"]:
            return False
        
        notification = {
            "type": "health",
            "health_score": health_score,
            "timestamp": datetime.now().isoformat()
        }
        
        self.notification_queue.put(notification)
        return True
    
    def _email_worker(self):
        """Background worker for sending emails"""
        while self.running:
            try:
                # Get notification from queue
                notification = self.notification_queue.get(timeout=10)
                
                # Send email based on notification type
                if notification["type"] == "alert":
                    self._send_alert_email(notification)
                elif notification["type"] == "report":
                    self._send_report_email(notification)
                elif notification["type"] == "backup":
                    self._send_backup_email(notification)
                elif notification["type"] == "health":
                    self._send_health_email(notification)
                
                # Mark task as done
                self.notification_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in email worker: {e}")
    
    def _send_alert_email(self, notification: Dict[str, Any]):
        """Send alert email"""
        try:
            subject = self.settings["templates"]["alert_subject"].format(
                alert_type=notification["alert_type"].title()
            )
            
            # Create HTML email body
            html_body = self._create_alert_html(notification)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings["from_email"]
            msg['To'] = ', '.join(self.settings["to_emails"])
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            self._send_email(msg)
            
        except Exception as e:
            print(f"Error sending alert email: {e}")
    
    def _send_report_email(self, notification: Dict[str, Any]):
        """Send report email"""
        try:
            subject = self.settings["templates"]["report_subject"].format(
                report_type=f"{notification['report_type'].title()} Report"
            )
            
            # Create HTML email body
            html_body = self._create_report_html(notification)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings["from_email"]
            msg['To'] = ', '.join(self.settings["to_emails"])
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Attach files if specified
            for attachment_path in notification.get("attachments", []):
                if os.path.exists(attachment_path):
                    self._attach_file(msg, attachment_path)
            
            # Send email
            self._send_email(msg)
            
        except Exception as e:
            print(f"Error sending report email: {e}")
    
    def _send_backup_email(self, notification: Dict[str, Any]):
        """Send backup completion email"""
        try:
            subject = self.settings["templates"]["backup_subject"].format(
                backup_name=notification["backup_name"]
            )
            
            # Create HTML email body
            html_body = self._create_backup_html(notification)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings["from_email"]
            msg['To'] = ', '.join(self.settings["to_emails"])
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            self._send_email(msg)
            
        except Exception as e:
            print(f"Error sending backup email: {e}")
    
    def _send_health_email(self, notification: Dict[str, Any]):
        """Send system health email"""
        try:
            subject = f"🏥 System Health Report - {notification['health_score']['overall']:.1f}/100"
            
            # Create HTML email body
            html_body = self._create_health_html(notification)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings["from_email"]
            msg['To'] = ', '.join(self.settings["to_emails"])
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            self._send_email(msg)
            
        except Exception as e:
            print(f"Error sending health email: {e}")
    
    def _send_email(self, msg: MIMEMultipart):
        """Send email using SMTP"""
        try:
            # Create SMTP session
            if self.settings["use_ssl"]:
                server = smtplib.SMTP_SSL(self.settings["smtp_server"], self.settings["smtp_port"])
            else:
                server = smtplib.SMTP(self.settings["smtp_server"], self.settings["smtp_port"])
                
                if self.settings["use_tls"]:
                    server.starttls()
            
            # Login with credentials
            server.login(self.settings["username"], self.settings["password"])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.settings["from_email"], self.settings["to_emails"], text)
            
            # Close connection
            server.quit()
            
        except Exception as e:
            print(f"SMTP error: {e}")
            raise
    
    def _create_alert_html(self, notification: Dict[str, Any]) -> str:
        """Create HTML content for alert email"""
        severity_colors = {
            "critical": "#ff4444",
            "warning": "#ffaa00",
            "info": "#00d4ff"
        }
        
        color = severity_colors.get(notification["severity"], "#00d4ff")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .footer {{ margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                .severity {{ font-weight: bold; color: {color}; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 System Alert</h1>
                <p>Alert Type: {notification['alert_type'].title()}</p>
                <p>Severity: <span class="severity">{notification['severity'].upper()}</span></p>
                <p class="timestamp">{notification['timestamp']}</p>
            </div>
            
            <div class="content">
                <h2>Alert Details</h2>
                <p>{notification['message']}</p>
        """
        
        # Add details if available
        if notification["details"]:
            html += "<h3>Additional Information</h3><ul>"
            for key, value in notification["details"].items():
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
            html += "</ul>"
        
        html += """
            </div>
            
            <div class="footer">
                <p>This is an automated alert from the System Performance Monitor.</p>
                <p>Please check your system dashboard for more details.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_report_html(self, notification: Dict[str, Any]) -> str:
        """Create HTML content for report email"""
        report_data = notification["report_data"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #00d4ff; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                .footer {{ margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 System Performance Report</h1>
                <p>Report Type: {notification['report_type'].title()}</p>
                <p class="timestamp">{notification['timestamp']}</p>
            </div>
            
            <div class="content">
                <h2>Performance Summary</h2>
        """
        
        # Add summary metrics if available
        if "summary" in report_data:
            summary = report_data["summary"]
            html += f"""
                <div class="metric">Average CPU: {summary.get('average_cpu', 'N/A'):.1f}%</div>
                <div class="metric">Peak CPU: {summary.get('max_cpu', 'N/A'):.1f}%</div>
                <div class="metric">Average Memory: {summary.get('average_memory', 'N/A'):.1f}%</div>
                <div class="metric">Peak Memory: {summary.get('max_memory', 'N/A'):.1f}%</div>
            """
        
        # Add health score if available
        if "health_score" in report_data:
            health = report_data["health_score"]
            html += f"""
                <h3>System Health Score</h3>
                <div class="metric">Overall: {health.get('overall', 'N/A'):.1f}/100</div>
                <div class="metric">Grade: {health.get('grade', 'N/A')}</div>
                <div class="metric">Status: {health.get('status', 'N/A')}</div>
            """
        
        html += """
            </div>
            
            <div class="footer">
                <p>This is an automated report from the System Performance Monitor.</p>
                <p>Please check your system dashboard for more detailed information.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_backup_html(self, notification: Dict[str, Any]) -> str:
        """Create HTML content for backup email"""
        backup_info = notification["backup_info"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #00ff88; color: #1a1a1a; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .footer {{ margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💾 Backup Complete</h1>
                <p>Backup Name: {notification['backup_name']}</p>
                <p class="timestamp">{notification['timestamp']}</p>
            </div>
            
            <div class="content">
                <h2>Backup Details</h2>
        """
        
        # Add backup components
        if "components" in backup_info:
            html += "<h3>Backed Up Components:</h3><ul>"
            for component, info in backup_info["components"].items():
                if isinstance(info, dict):
                    html += f"<li><strong>{component.title()}:</strong> {info.get('file', 'N/A')} ({info.get('size', 0)} bytes)</li>"
                else:
                    html += f"<li><strong>{component.title()}:</strong> {info}</li>"
            html += "</ul>"
        
        html += f"""
                <p><strong>Created:</strong> {backup_info.get('created_at', 'N/A')}</p>
                <p><strong>Version:</strong> {backup_info.get('version', 'N/A')}</p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from the System Performance Monitor.</p>
                <p>Your backup has been successfully completed.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_health_html(self, notification: Dict[str, Any]) -> str:
        """Create HTML content for health email"""
        health_score = notification["health_score"]
        
        # Determine color based on score
        score = health_score.get("overall", 0)
        if score >= 85:
            color = "#00ff88"
        elif score >= 70:
            color = "#ffaa00"
        else:
            color = "#ff4444"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                .footer {{ margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 System Health Report</h1>
                <p>Overall Score: {health_score.get('overall', 'N/A'):.1f}/100</p>
                <p>Grade: {health_score.get('grade', 'N/A')}</p>
                <p>Status: {health_score.get('status', 'N/A')}</p>
                <p class="timestamp">{notification['timestamp']}</p>
            </div>
            
            <div class="content">
                <h2>Component Health Scores</h2>
        """
        
        # Add component scores
        if "components" in health_score:
            for component, score in health_score["components"].items():
                html += f'<div class="metric">{component.title()}: {score:.1f}/100</div>'
        
        html += """
            </div>
            
            <div class="footer">
                <p>This is an automated health report from the System Performance Monitor.</p>
                <p>Please check your system dashboard for more detailed information.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach file to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            print(f"Error attaching file {file_path}: {e}")
    
    def test_email_settings(self) -> Dict[str, Any]:
        """Test email settings by sending a test email"""
        try:
            if not self.settings["enabled"]:
                return {"success": False, "error": "Email notifications are disabled"}
            
            if not self.settings["to_emails"]:
                return {"success": False, "error": "No recipient emails configured"}
            
            # Create test email
            msg = MIMEMultipart()
            msg['Subject'] = "🧪 Test Email - System Performance Monitor"
            msg['From'] = self.settings["from_email"]
            msg['To'] = ', '.join(self.settings["to_emails"])
            
            # Create HTML test content
            html_content = """
            <!DOCTYPE html>
            <html>
            <head><style>body {font-family: Arial; margin: 20px;}</style></head>
            <body>
                <h2>🧪 Email Test Successful</h2>
                <p>This is a test email to verify your email notification settings.</p>
                <p>If you received this email, your email configuration is working correctly.</p>
                <p>Test Time: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send test email
            self._send_email(msg)
            
            return {"success": True, "message": "Test email sent successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_notification_queue_status(self) -> Dict[str, Any]:
        """Get notification queue status"""
        return {
            "queue_size": self.notification_queue.qsize(),
            "service_running": self.running,
            "email_enabled": self.settings["enabled"],
            "configured_recipients": len(self.settings["to_emails"])
        }
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update email settings"""
        try:
            # Validate required fields
            if new_settings.get("enabled"):
                required_fields = ["smtp_server", "smtp_port", "username", "password", "from_email", "to_emails"]
                for field in required_fields:
                    if not new_settings.get(field):
                        return False
                
                # Validate email addresses
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                if not re.match(email_pattern, new_settings["from_email"]):
                    return False
                
                for email in new_settings["to_emails"]:
                    if not re.match(email_pattern, email):
                        return False
            
            # Update settings
            self.settings.update(new_settings)
            self.save_settings(self.settings)
            
            # Restart service if enabled/disabled changed
            if new_settings.get("enabled") != self.settings.get("enabled"):
                if new_settings.get("enabled"):
                    self.start_email_service()
                else:
                    self.stop_email_service()
            
            return True
            
        except Exception as e:
            print(f"Error updating email settings: {e}")
            return False
