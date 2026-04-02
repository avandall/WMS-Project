"""Security audit processor for monitoring database security events."""

import os
import time
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from sqlalchemy import create_engine, text
from app.core.logging import get_logger

logger = get_logger(__name__)

class SecurityAuditProcessor:
    """Processes security audit logs and generates alerts."""
    
    def __init__(self):
        self.db_url = os.getenv("READONLY_DATABASE_URL")
        self.log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", "90"))
        self.failed_login_threshold = int(os.getenv("ALERT_THRESHOLD_FAILED_LOGINS", "10"))
        self.slow_query_threshold = int(os.getenv("ALERT_THRESHOLD_SLOW_QUERIES", "5"))
        
        # Email configuration (optional)
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.alert_email = os.getenv("ALERT_EMAIL")
    
    def process_audit_logs(self) -> None:
        """Process audit logs and generate security alerts."""
        try:
            engine = create_engine(self.db_url)
            
            # Get recent audit events
            cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
            
            # Check for suspicious patterns
            self._check_failed_logins(engine)
            self._check_privilege_escalation(engine)
            self._check_unusual_activity(engine)
            self._check_slow_queries(engine)
            self._check_data_access_patterns(engine)
            
            # Clean old audit logs
            self._cleanup_old_logs(engine, cutoff_date)
            
            logger.info("Security audit processing completed")
            
        except Exception as e:
            logger.error(f"Security audit processing failed: {str(e)}")
    
    def _check_failed_logins(self, engine) -> None:
        """Check for failed login patterns."""
        query = """
            SELECT user_name, COUNT(*) as failed_count, MAX(timestamp) as last_attempt
            FROM audit_logs 
            WHERE operation = 'LOGIN_FAILED' 
            AND timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY user_name
            HAVING COUNT(*) >= :threshold
        """
        
        result = engine.execute(text(query), {"threshold": self.failed_login_threshold})
        failed_logins = result.fetchall()
        
        if failed_logins:
            alert_msg = "🚨 SECURITY ALERT: Multiple failed login attempts detected\n\n"
            for login in failed_logins:
                alert_msg += f"User: {login['user_name']}, Failed attempts: {login['failed_count']}, Last attempt: {login['last_attempt']}\n"
            
            self._send_alert("Multiple Failed Logins", alert_msg)
            logger.warning(f"Security alert: Multiple failed logins detected: {failed_logins}")
    
    def _check_privilege_escalation(self, engine) -> None:
        """Check for privilege escalation attempts."""
        query = """
            SELECT user_name, table_name, operation, timestamp
            FROM audit_logs 
            WHERE operation IN ('DELETE', 'UPDATE', 'INSERT')
            AND table_name IN ('users', 'audit_logs', 'pg_roles', 'pg_authid')
            AND timestamp >= NOW() - INTERVAL '24 hours'
            ORDER BY timestamp DESC
            LIMIT 10
        """
        
        result = engine.execute(text(query))
        suspicious_ops = result.fetchall()
        
        if suspicious_ops:
            alert_msg = "🚨 SECURITY ALERT: Privilege escalation attempts detected\n\n"
            for op in suspicious_ops:
                alert_msg += f"User: {op['user_name']}, Table: {op['table_name']}, Operation: {op['operation']}, Time: {op['timestamp']}\n"
            
            self._send_alert("Privilege Escalation", alert_msg)
            logger.critical(f"Security alert: Privilege escalation attempts: {suspicious_ops}")
    
    def _check_unusual_activity(self, engine) -> None:
        """Check for unusual database activity patterns."""
        query = """
            SELECT 
                user_name,
                COUNT(*) as operation_count,
                COUNT(DISTINCT table_name) as table_count,
                MIN(timestamp) as first_activity,
                MAX(timestamp) as last_activity
            FROM audit_logs 
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY user_name
            HAVING COUNT(*) > 100 OR COUNT(DISTINCT table_name) > 10
        """
        
        result = engine.execute(text(query))
        unusual_activity = result.fetchall()
        
        if unusual_activity:
            alert_msg = "🚨 SECURITY ALERT: Unusual database activity detected\n\n"
            for activity in unusual_activity:
                alert_msg += f"User: {activity['user_name']}, Operations: {activity['operation_count']}, Tables: {activity['table_count']}\n"
            
            self._send_alert("Unusual Activity", alert_msg)
            logger.warning(f"Security alert: Unusual activity detected: {unusual_activity}")
    
    def _check_slow_queries(self, engine) -> None:
        """Check for unusually slow queries."""
        query = """
            SELECT query, calls, total_time, mean_time, rows
            FROM pg_stat_statements 
            WHERE mean_time > :threshold 
            AND calls > 1
            ORDER BY mean_time DESC 
            LIMIT 10
        """
        
        result = engine.execute(text(query), {"threshold": self.slow_query_threshold})
        slow_queries = result.fetchall()
        
        if slow_queries:
            alert_msg = "🚨 PERFORMANCE ALERT: Slow queries detected\n\n"
            for query in slow_queries:
                alert_msg += f"Query: {query['query'][:100]}..., Mean time: {query['mean_time']:.2f}ms, Calls: {query['calls']}\n"
            
            self._send_alert("Slow Queries", alert_msg)
            logger.warning(f"Performance alert: Slow queries detected: {slow_queries}")
    
    def _check_data_access_patterns(self, engine) -> None:
        """Check for unusual data access patterns."""
        query = """
            SELECT 
                user_name,
                table_name,
                operation,
                COUNT(*) as access_count,
                COUNT(DISTINCT record_id) as unique_records
            FROM audit_logs 
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY user_name, table_name, operation
            HAVING COUNT(*) > 1000
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """
        
        result = engine.execute(text(query))
        excessive_access = result.fetchall()
        
        if excessive_access:
            alert_msg = "🚨 SECURITY ALERT: Excessive data access detected\n\n"
            for access in excessive_access:
                alert_msg += f"User: {access['user_name']}, Table: {access['table_name']}, Operation: {access['operation']}, Count: {access['access_count']}\n"
            
            self._send_alert("Excessive Data Access", alert_msg)
            logger.warning(f"Security alert: Excessive data access: {excessive_access}")
    
    def _cleanup_old_logs(self, engine, cutoff_date) -> None:
        """Clean up old audit logs to manage storage."""
        try:
            delete_query = "DELETE FROM audit_logs WHERE timestamp < :cutoff_date"
            result = engine.execute(text(delete_query), {"cutoff_date": cutoff_date})
            deleted_count = result.rowcount
            
            logger.info(f"Cleaned up {deleted_count} old audit log entries")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old audit logs: {str(e)}")
    
    def _send_alert(self, alert_type: str, message: str) -> None:
        """Send security alert via email if configured."""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.alert_email]):
            logger.info(f"Alert configured but email not set: {alert_type}")
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = f"WMS Security Alert: {alert_type}"
            
            body = MimeText(message, 'plain')
            msg.attach(body)
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Security alert sent: {alert_type}")
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
    
    def generate_security_report(self) -> dict:
        """Generate comprehensive security report."""
        try:
            engine = create_engine(self.db_url)
            
            # Get statistics for different time periods
            queries = {
                "last_24h": """
                    SELECT user_name, COUNT(*) as operations, COUNT(DISTINCT table_name) as tables
                    FROM audit_logs 
                    WHERE timestamp >= NOW() - INTERVAL '24 hours'
                    GROUP BY user_name
                """,
                "last_7d": """
                    SELECT user_name, COUNT(*) as operations, COUNT(DISTINCT table_name) as tables
                    FROM audit_logs 
                    WHERE timestamp >= NOW() - INTERVAL '7 days'
                    GROUP BY user_name
                """,
                "failed_logins_24h": """
                    SELECT user_name, COUNT(*) as failed_attempts
                    FROM audit_logs 
                    WHERE operation = 'LOGIN_FAILED' 
                    AND timestamp >= NOW() - INTERVAL '24 hours'
                    GROUP BY user_name
                """
            }
            
            report = {"timestamp": datetime.now().isoformat(), "period": "24 hours"}
            
            for period, query in queries.items():
                result = engine.execute(text(query))
                report[period] = [dict(row) for row in result.fetchall()]
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate security report: {str(e)}")
            return {"error": str(e)}
    
    def run_continuous_monitoring(self) -> None:
        """Run continuous security monitoring."""
        logger.info("Starting continuous security monitoring")
        
        while True:
            try:
                self.process_audit_logs()
                
                # Generate hourly report
                current_time = datetime.now()
                if current_time.minute == 0:
                    report = self.generate_security_report()
                    logger.info(f"Hourly security report generated: {json.dumps(report, default=str)}")
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("Security monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Security monitoring error: {str(e)}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    processor = SecurityAuditProcessor()
    processor.run_continuous_monitoring()
