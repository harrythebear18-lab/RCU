#!/usr/bin/env python3
"""
Machine Learning Features
Predictive resource allocation, usage pattern learning, and performance impact analysis.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import sqlite3
import threading
import time
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

class MachineLearningManager:
    """Machine Learning Manager for predictive analytics"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'system_monitoring.db')
        self.models_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'ml_settings.json')
        
        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)
        
        # ML settings
        self.settings = self.load_settings()
        
        # Models
        self.models = {}
        self.scalers = {}
        
        # Training data
        self.training_data = []
        self.prediction_cache = {}
        
        # Initialize models
        self.initialize_models()
        
        # Load trained models
        self.load_models()
        
        # Training thread
        self.training_active = False
        self.training_thread = None
    
    def load_settings(self) -> Dict[str, Any]:
        """Load ML settings"""
        default_settings = {
            'training_enabled': True,
            'prediction_enabled': True,
            'anomaly_detection_enabled': True,
            'model_retrain_interval': 24,  # hours
            'min_training_samples': 100,
            'prediction_horizon': 60,  # minutes
            'anomaly_threshold': 0.1,
            'feature_importance_threshold': 0.05
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
        """Save ML settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def initialize_models(self):
        """Initialize ML models"""
        # CPU usage prediction model
        self.models['cpu_usage'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['cpu_usage'] = StandardScaler()
        
        # Memory usage prediction model
        self.models['memory_usage'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['memory_usage'] = StandardScaler()
        
        # GPU usage prediction model
        self.models['gpu_usage'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['gpu_usage'] = StandardScaler()
        
        # Anomaly detection model
        self.models['anomaly_detection'] = IsolationForest(contamination=0.1, random_state=42)
        self.scalers['anomaly_detection'] = StandardScaler()
        
        # Performance impact model
        self.models['performance_impact'] = LinearRegression()
        self.scalers['performance_impact'] = StandardScaler()
        
        # Resource allocation model
        self.models['resource_allocation'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['resource_allocation'] = StandardScaler()
    
    def load_models(self):
        """Load trained models"""
        for model_name in self.models.keys():
            model_file = os.path.join(self.models_dir, f'{model_name}.pkl')
            scaler_file = os.path.join(self.models_dir, f'{model_name}_scaler.pkl')
            
            try:
                if os.path.exists(model_file):
                    self.models[model_name] = joblib.load(model_file)
                
                if os.path.exists(scaler_file):
                    self.scalers[model_name] = joblib.load(scaler_file)
                    
            except Exception:
                pass  # Models not trained yet
    
    def save_models(self):
        """Save trained models"""
        for model_name, model in self.models.items():
            model_file = os.path.join(self.models_dir, f'{model_name}.pkl')
            scaler_file = os.path.join(self.models_dir, f'{model_name}_scaler.pkl')
            
            try:
                joblib.dump(model, model_file)
                joblib.dump(self.scalers[model_name], scaler_file)
            except Exception:
                pass
    
    def collect_training_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect training data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get historical performance data
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, cpu_usage, memory_usage, gpu_usage, gpu_temp,
                       network_sent, network_recv, disk_read, disk_write, health_score
                FROM system_metrics
                WHERE timestamp > ?
                ORDER BY timestamp
            ''', (cutoff_time.isoformat(),))
            
            data = cursor.fetchall()
            conn.close()
            
            # Convert to training format
            training_data = []
            for row in data:
                timestamp = datetime.fromisoformat(row[0])
                
                # Extract features
                hour_of_day = timestamp.hour
                day_of_week = timestamp.weekday()
                
                # Create feature vector
                features = {
                    'timestamp': timestamp.isoformat(),
                    'hour_of_day': hour_of_day,
                    'day_of_week': day_of_week,
                    'cpu_usage': row[1] if row[1] is not None else 0,
                    'memory_usage': row[2] if row[2] is not None else 0,
                    'gpu_usage': row[3] if row[3] is not None else 0,
                    'gpu_temp': row[4] if row[4] is not None else 0,
                    'network_sent': row[5] if row[5] is not None else 0,
                    'network_recv': row[6] if row[6] is not None else 0,
                    'disk_read': row[7] if row[7] is not None else 0,
                    'disk_write': row[8] if row[8] is not None else 0,
                    'health_score': row[9] if row[9] is not None else 50
                }
                
                training_data.append(features)
            
            return training_data
            
        except Exception as e:
            print(f"Error collecting training data: {e}")
            return []
    
    def prepare_features(self, data: List[Dict[str, Any]], target_column: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for training"""
        if not data:
            return np.array([]), np.array([])
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Feature engineering
        features = []
        targets = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Time-based features
            hour_sin = np.sin(2 * np.pi * row['hour_of_day'] / 24)
            hour_cos = np.cos(2 * np.pi * row['hour_of_day'] / 24)
            day_sin = np.sin(2 * np.pi * row['day_of_week'] / 7)
            day_cos = np.cos(2 * np.pi * row['day_of_week'] / 7)
            
            # Performance features
            cpu_usage = row['cpu_usage']
            memory_usage = row['memory_usage']
            gpu_usage = row['gpu_usage']
            gpu_temp = row['gpu_temp']
            
            # Network features
            network_total = row['network_sent'] + row['network_recv']
            network_ratio = row['network_sent'] / (row['network_recv'] + 1) if row['network_recv'] > 0 else 0
            
            # Disk features
            disk_total = row['disk_read'] + row['disk_write']
            disk_ratio = row['disk_read'] / (row['disk_write'] + 1) if row['disk_write'] > 0 else 0
            
            # Health score
            health_score = row['health_score']
            
            # Create feature vector
            feature_vector = [
                hour_sin, hour_cos, day_sin, day_cos,
                cpu_usage, memory_usage, gpu_usage, gpu_temp,
                network_total, network_ratio, disk_total, disk_ratio,
                health_score
            ]
            
            features.append(feature_vector)
            targets.append(row[target_column])
        
        return np.array(features), np.array(targets)
    
    def train_cpu_usage_model(self) -> Dict[str, Any]:
        """Train CPU usage prediction model"""
        data = self.collect_training_data()
        
        if len(data) < self.settings.get('min_training_samples', 100):
            return {'status': 'insufficient_data', 'samples': len(data)}
        
        # Prepare features
        X, y = self.prepare_features(data, 'cpu_usage')
        
        if len(X) == 0:
            return {'status': 'no_features'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scalers['cpu_usage'].fit_transform(X_train)
        X_test_scaled = self.scalers['cpu_usage'].transform(X_test)
        
        # Train model
        self.models['cpu_usage'].fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.models['cpu_usage'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        feature_names = [
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'cpu_usage', 'memory_usage', 'gpu_usage', 'gpu_temp',
            'network_total', 'network_ratio', 'disk_total', 'disk_ratio',
            'health_score'
        ]
        
        importance = self.models['cpu_usage'].feature_importances_
        feature_importance = dict(zip(feature_names, importance))
        
        return {
            'status': 'success',
            'mse': mse,
            'r2_score': r2,
            'feature_importance': feature_importance,
            'samples': len(data)
        }
    
    def train_memory_usage_model(self) -> Dict[str, Any]:
        """Train memory usage prediction model"""
        data = self.collect_training_data()
        
        if len(data) < self.settings.get('min_training_samples', 100):
            return {'status': 'insufficient_data', 'samples': len(data)}
        
        # Prepare features
        X, y = self.prepare_features(data, 'memory_usage')
        
        if len(X) == 0:
            return {'status': 'no_features'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scalers['memory_usage'].fit_transform(X_train)
        X_test_scaled = self.scalers['memory_usage'].transform(X_test)
        
        # Train model
        self.models['memory_usage'].fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.models['memory_usage'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'status': 'success',
            'mse': mse,
            'r2_score': r2,
            'samples': len(data)
        }
    
    def train_gpu_usage_model(self) -> Dict[str, Any]:
        """Train GPU usage prediction model"""
        data = self.collect_training_data()
        
        if len(data) < self.settings.get('min_training_samples', 100):
            return {'status': 'insufficient_data', 'samples': len(data)}
        
        # Filter data with GPU information
        gpu_data = [row for row in data if row.get('gpu_usage', 0) > 0]
        
        if len(gpu_data) < 50:
            return {'status': 'insufficient_gpu_data', 'samples': len(gpu_data)}
        
        # Prepare features
        X, y = self.prepare_features(gpu_data, 'gpu_usage')
        
        if len(X) == 0:
            return {'status': 'no_features'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scalers['gpu_usage'].fit_transform(X_train)
        X_test_scaled = self.scalers['gpu_usage'].transform(X_test)
        
        # Train model
        self.models['gpu_usage'].fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.models['gpu_usage'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'status': 'success',
            'mse': mse,
            'r2_score': r2,
            'samples': len(gpu_data)
        }
    
    def train_anomaly_detection_model(self) -> Dict[str, Any]:
        """Train anomaly detection model"""
        data = self.collect_training_data()
        
        if len(data) < self.settings.get('min_training_samples', 100):
            return {'status': 'insufficient_data', 'samples': len(data)}
        
        # Prepare features for anomaly detection
        features = []
        
        for row in data:
            feature_vector = [
                row['cpu_usage'],
                row['memory_usage'],
                row['gpu_usage'] if row.get('gpu_usage', 0) > 0 else 0,
                row['gpu_temp'] if row.get('gpu_temp', 0) > 0 else 0,
                row['network_sent'] + row['network_recv'],
                row['disk_read'] + row['disk_write'],
                row['health_score']
            ]
            features.append(feature_vector)
        
        X = np.array(features)
        
        # Scale features
        X_scaled = self.scalers['anomaly_detection'].fit_transform(X)
        
        # Train model
        self.models['anomaly_detection'].fit(X_scaled)
        
        return {
            'status': 'success',
            'samples': len(data)
        }
    
    def predict_cpu_usage(self, minutes_ahead: int = 60) -> Dict[str, Any]:
        """Predict CPU usage"""
        if not self.settings.get('prediction_enabled', True):
            return {'status': 'disabled'}
        
        try:
            # Get current data
            current_data = self.collect_training_data(hours=1)
            
            if not current_data:
                return {'status': 'no_data'}
            
            # Prepare features for prediction
            current_row = current_data[-1]  # Use most recent data
            timestamp = datetime.fromisoformat(current_row['timestamp'])
            future_timestamp = timestamp + timedelta(minutes=minutes_ahead)
            
            # Create feature vector for future time
            hour_sin = np.sin(2 * np.pi * future_timestamp.hour / 24)
            hour_cos = np.cos(2 * np.pi * future_timestamp.hour / 24)
            day_sin = np.sin(2 * np.pi * future_timestamp.weekday() / 7)
            day_cos = np.cos(2 * np.pi * future_timestamp.weekday() / 7)
            
            feature_vector = [
                hour_sin, hour_cos, day_sin, day_cos,
                current_row['cpu_usage'],
                current_row['memory_usage'],
                current_row['gpu_usage'],
                current_row['gpu_temp'],
                current_row['network_sent'] + current_row['network_recv'],
                current_row['network_sent'] / (current_row['network_recv'] + 1) if current_row['network_recv'] > 0 else 0,
                current_row['disk_read'] + current_row['disk_write'],
                current_row['disk_read'] / (current_row['disk_write'] + 1) if current_row['disk_write'] > 0 else 0,
                current_row['health_score']
            ]
            
            # Scale features
            X = np.array([feature_vector])
            X_scaled = self.scalers['cpu_usage'].transform(X)
            
            # Make prediction
            prediction = self.models['cpu_usage'].predict(X_scaled)[0]
            
            # Ensure prediction is within valid range
            prediction = max(0, min(100, prediction))
            
            return {
                'status': 'success',
                'predicted_usage': prediction,
                'minutes_ahead': minutes_ahead,
                'timestamp': future_timestamp.isoformat()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def predict_memory_usage(self, minutes_ahead: int = 60) -> Dict[str, Any]:
        """Predict memory usage"""
        if not self.settings.get('prediction_enabled', True):
            return {'status': 'disabled'}
        
        try:
            # Get current data
            current_data = self.collect_training_data(hours=1)
            
            if not current_data:
                return {'status': 'no_data'}
            
            # Prepare features for prediction
            current_row = current_data[-1]
            timestamp = datetime.fromisoformat(current_row['timestamp'])
            future_timestamp = timestamp + timedelta(minutes=minutes_ahead)
            
            # Create feature vector
            hour_sin = np.sin(2 * np.pi * future_timestamp.hour / 24)
            hour_cos = np.cos(2 * np.pi * future_timestamp.hour / 24)
            day_sin = np.sin(2 * np.pi * future_timestamp.weekday() / 7)
            day_cos = np.cos(2 * np.pi * future_timestamp.weekday() / 7)
            
            feature_vector = [
                hour_sin, hour_cos, day_sin, day_cos,
                current_row['cpu_usage'],
                current_row['memory_usage'],
                current_row['gpu_usage'],
                current_row['gpu_temp'],
                current_row['network_sent'] + current_row['network_recv'],
                current_row['network_sent'] / (current_row['network_recv'] + 1) if current_row['network_recv'] > 0 else 0,
                current_row['disk_read'] + current_row['disk_write'],
                current_row['disk_read'] / (current_row['disk_write'] + 1) if current_row['disk_write'] > 0 else 0,
                current_row['health_score']
            ]
            
            # Scale features
            X = np.array([feature_vector])
            X_scaled = self.scalers['memory_usage'].transform(X)
            
            # Make prediction
            prediction = self.models['memory_usage'].predict(X_scaled)[0]
            
            # Ensure prediction is within valid range
            prediction = max(0, min(100, prediction))
            
            return {
                'status': 'success',
                'predicted_usage': prediction,
                'minutes_ahead': minutes_ahead,
                'timestamp': future_timestamp.isoformat()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def detect_anomalies(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in current metrics"""
        if not self.settings.get('anomaly_detection_enabled', True):
            return {'status': 'disabled'}
        
        try:
            # Prepare features
            feature_vector = [
                current_metrics.get('cpu_usage', 0),
                current_metrics.get('memory_usage', 0),
                current_metrics.get('gpu_usage', 0),
                current_metrics.get('gpu_temp', 0),
                current_metrics.get('network_sent', 0) + current_metrics.get('network_recv', 0),
                current_metrics.get('disk_read', 0) + current_metrics.get('disk_write', 0),
                current_metrics.get('health_score', 50)
            ]
            
            # Scale features
            X = np.array([feature_vector])
            X_scaled = self.scalers['anomaly_detection'].transform(X)
            
            # Detect anomaly
            anomaly_score = self.models['anomaly_detection'].decision_function(X_scaled)[0]
            is_anomaly = self.models['anomaly_detection'].predict(X_scaled)[0] == -1
            
            threshold = self.settings.get('anomaly_threshold', 0.1)
            
            return {
                'status': 'success',
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'threshold': threshold,
                'metrics': current_metrics
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def analyze_usage_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze usage patterns"""
        try:
            data = self.collect_training_data(hours=days * 24)
            
            if not data:
                return {'status': 'no_data'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(data)
            
            # Hourly patterns
            hourly_cpu = df.groupby('hour_of_day')['cpu_usage'].mean()
            hourly_memory = df.groupby('hour_of_day')['memory_usage'].mean()
            
            # Daily patterns
            daily_cpu = df.groupby('day_of_week')['cpu_usage'].mean()
            daily_memory = df.groupby('day_of_week')['memory_usage'].mean()
            
            # Peak hours
            peak_cpu_hour = hourly_cpu.idxmax()
            peak_memory_hour = hourly_memory.idxmax()
            
            # Low usage hours
            low_cpu_hour = hourly_cpu.idxmin()
            low_memory_hour = hourly_memory.idxmin()
            
            # Statistics
            cpu_mean = df['cpu_usage'].mean()
            cpu_std = df['cpu_usage'].std()
            memory_mean = df['memory_usage'].mean()
            memory_std = df['memory_usage'].std()
            
            return {
                'status': 'success',
                'period_days': days,
                'hourly_patterns': {
                    'cpu': hourly_cpu.to_dict(),
                    'memory': hourly_memory.to_dict()
                },
                'daily_patterns': {
                    'cpu': daily_cpu.to_dict(),
                    'memory': daily_memory.to_dict()
                },
                'peak_hours': {
                    'cpu': int(peak_cpu_hour),
                    'memory': int(peak_memory_hour)
                },
                'low_hours': {
                    'cpu': int(low_cpu_hour),
                    'memory': int(low_memory_hour)
                },
                'statistics': {
                    'cpu_mean': float(cpu_mean),
                    'cpu_std': float(cpu_std),
                    'memory_mean': float(memory_mean),
                    'memory_std': float(memory_std)
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_recommendations(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Get ML-based recommendations"""
        recommendations = []
        
        try:
            # Detect anomalies
            anomaly_result = self.detect_anomalies(current_metrics)
            
            if anomaly_result.get('is_anomaly'):
                recommendations.append("⚠️ Anomalous system behavior detected - consider running diagnostics")
            
            # Predict future usage
            cpu_pred = self.predict_cpu_usage(30)
            mem_pred = self.predict_memory_usage(30)
            
            if cpu_pred.get('status') == 'success':
                predicted_cpu = cpu_pred['predicted_usage']
                if predicted_cpu > 80:
                    recommendations.append("🔥 High CPU usage predicted in 30 minutes - consider optimization")
                elif predicted_cpu > 60:
                    recommendations.append("⚡ Moderate CPU usage predicted - monitor closely")
            
            if mem_pred.get('status') == 'success':
                predicted_memory = mem_pred['predicted_usage']
                if predicted_memory > 85:
                    recommendations.append("🧠 High memory usage predicted - consider memory cleanup")
                elif predicted_memory > 70:
                    recommendations.append("💾 Moderate memory usage predicted - monitor closely")
            
            # Current metrics analysis
            cpu_usage = current_metrics.get('cpu_usage', 0)
            memory_usage = current_metrics.get('memory_usage', 0)
            health_score = current_metrics.get('health_score', 50)
            
            if cpu_usage > 90:
                recommendations.append("🚨 Critical CPU usage - immediate action required")
            elif cpu_usage > 75:
                recommendations.append("⚠️ High CPU usage - consider optimization")
            
            if memory_usage > 90:
                recommendations.append("🚨 Critical memory usage - immediate action required")
            elif memory_usage > 80:
                recommendations.append("⚠️ High memory usage - consider cleanup")
            
            if health_score < 30:
                recommendations.append("💔 Poor system health - comprehensive optimization recommended")
            elif health_score < 50:
                recommendations.append("🏥 Low system health - consider maintenance")
            
            # Pattern-based recommendations
            patterns = self.analyze_usage_patterns(1)
            if patterns.get('status') == 'success':
                peak_cpu_hour = patterns['peak_hours']['cpu']
                current_hour = datetime.now().hour
                
                if abs(current_hour - peak_cpu_hour) <= 1:
                    recommendations.append("⏰ Peak usage hour detected - expect higher resource usage")
            
        except Exception as e:
            recommendations.append(f"❌ Recommendation generation failed: {e}")
        
        return recommendations
    
    def start_training(self):
        """Start model training in background"""
        if self.training_active:
            return
        
        self.training_active = True
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()
    
    def stop_training(self):
        """Stop model training"""
        self.training_active = False
        if self.training_thread:
            self.training_thread.join(timeout=5)
    
    def _training_loop(self):
        """Training loop"""
        while self.training_active:
            try:
                # Train CPU model
                cpu_result = self.train_cpu_usage_model()
                print(f"CPU model training: {cpu_result.get('status')}")
                
                # Train memory model
                memory_result = self.train_memory_usage_model()
                print(f"Memory model training: {memory_result.get('status')}")
                
                # Train GPU model
                gpu_result = self.train_gpu_usage_model()
                print(f"GPU model training: {gpu_result.get('status')}")
                
                # Train anomaly detection model
                anomaly_result = self.train_anomaly_detection_model()
                print(f"Anomaly detection training: {anomaly_result.get('status')}")
                
                # Save models
                self.save_models()
                
                # Wait for next training cycle
                interval_hours = self.settings.get('model_retrain_interval', 24)
                time.sleep(interval_hours * 3600)
                
            except Exception as e:
                print(f"Training error: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get model training status"""
        status = {
            'training_active': self.training_active,
            'models': {}
        }
        
        for model_name in self.models.keys():
            model_file = os.path.join(self.models_dir, f'{model_name}.pkl')
            status['models'][model_name] = {
                'trained': os.path.exists(model_file),
                'file_exists': os.path.exists(model_file)
            }
        
        return status

# Global ML manager instance
ml_manager = MachineLearningManager()

# Convenience functions
def predict_cpu_usage(minutes_ahead: int = 60):
    """Predict CPU usage"""
    return ml_manager.predict_cpu_usage(minutes_ahead)

def predict_memory_usage(minutes_ahead: int = 60):
    """Predict memory usage"""
    return ml_manager.predict_memory_usage(minutes_ahead)

def detect_anomalies(metrics: Dict[str, Any]):
    """Detect anomalies"""
    return ml_manager.detect_anomalies(metrics)

def get_recommendations(metrics: Dict[str, Any]):
    """Get recommendations"""
    return ml_manager.get_recommendations(metrics)

def analyze_patterns(days: int = 7):
    """Analyze usage patterns"""
    return ml_manager.analyze_usage_patterns(days)

if __name__ == '__main__':
    # Test machine learning features
    print("Testing Machine Learning Features")
    print(f"Training enabled: {ml_manager.settings.get('training_enabled')}")
    print(f"Prediction enabled: {ml_manager.settings.get('prediction_enabled')}")
    print(f"Anomaly detection enabled: {ml_manager.settings.get('anomaly_detection_enabled')}")
    
    # Test model status
    status = ml_manager.get_model_status()
    print(f"Model status: {status}")
    
    # Test predictions (if models are trained)
    cpu_pred = predict_cpu_usage(30)
    print(f"CPU prediction: {cpu_pred.get('status')}")
    
    mem_pred = predict_memory_usage(30)
    print(f"Memory prediction: {mem_pred.get('status')}")
    
    # Test anomaly detection
    test_metrics = {
        'cpu_usage': 75,
        'memory_usage': 60,
        'gpu_usage': 30,
        'gpu_temp': 65,
        'network_sent': 1000,
        'network_recv': 2000,
        'disk_read': 500,
        'disk_write': 300,
        'health_score': 75
    }
    
    anomaly_result = detect_anomalies(test_metrics)
    print(f"Anomaly detection: {anomaly_result.get('status')}")
    
    # Test recommendations
    recommendations = get_recommendations(test_metrics)
    print(f"Recommendations: {len(recommendations)} generated")
    for rec in recommendations:
        print(f"  {rec}")
