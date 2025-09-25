import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
import requests
from prometheus_client import start_http_server, Gauge
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
SYSTEM_HEALTH = Gauge('system_health_status', 'Overall system health status (1 for healthy, 0 for unhealthy)')
DATABASE_CONNECTION = Gauge('database_connection_status', 'Database connection status')
STREAMING_SERVICE_STATUS = Gauge('streaming_service_status', 'Market data streaming service status')

class Alerter:
    """Handles sending alerts via different channels."""
    @staticmethod
    def send_slack_alert(message: str):
        """Sends an alert to a Slack channel."""
        webhook_url = settings.SLACK_WEBHOOK_URL
        if not webhook_url:
            logger.warning("Slack webhook URL not configured. Cannot send alert.")
            return
        try:
            payload = {'text': f":warning: Alert: {message}"}
            requests.post(webhook_url, json=payload, timeout=10)
            logger.info("Slack alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    @staticmethod
    def send_email_alert(subject: str, body: str):
        """Sends an email alert."""
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.ALERT_EMAIL_TO]):
            logger.warning("SMTP settings not fully configured. Cannot send email alert.")
            return
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_USER
        msg['To'] = settings.ALERT_EMAIL_TO

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                logger.info("Email alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

class MonitoringSystem:
    """
    Monitors system components, exposes Prometheus metrics, and triggers alerts.
    """
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.thresholds = {
            'cpu_usage': 80, # percent
            'memory_usage': 85, # percent
        }
        self.is_healthy = True

    async def check_system_health(self):
        """Periodically checks the health of various system components."""
        while True:
            try:
                # Example checks (replace with actual health checks)
                db_ok = await self._check_database()
                streaming_ok = self._check_streaming_service()
                
                # Update overall health
                self.is_healthy = db_ok and streaming_ok
                SYSTEM_HEALTH.set(1 if self.is_healthy else 0)

                if not self.is_healthy:
                    alert_message = "System health check failed!"
                    if not db_ok:
                        alert_message += " Database connection is down."
                    if not streaming_ok:
                        alert_message += " Streaming service is down."
                    
                    Alerter.send_slack_alert(alert_message)
                    Alerter.send_email_alert("System Alert: Health Check Failed", alert_message)

            except Exception as e:
                logger.error(f"Error during health check: {e}")
                SYSTEM_HEALTH.set(0)
                Alerter.send_slack_alert(f"Monitoring system encountered an error: {e}")

            await asyncio.sleep(self.check_interval)

    async def _check_database(self) -> bool:
        """Checks the database connection status."""
        # This should integrate with the DatabaseConnector or a health check endpoint
        # For now, we'll simulate it.
        is_connected = True # Replace with actual check
        DATABASE_CONNECTION.set(1 if is_connected else 0)
        if not is_connected:
            logger.warning("Database connection check failed.")
        return is_connected

    def _check_streaming_service(self) -> bool:
        """Checks the streaming service status."""
        # This should check if the streaming service is running and receiving data
        is_streaming = True # Replace with actual check
        STREAMING_SERVICE_STATUS.set(1 if is_streaming else 0)
        if not is_streaming:
            logger.warning("Streaming service check failed.")
        return is_streaming

    def start(self):
        """Starts the monitoring system."""
        logger.info("Starting monitoring system...")
        # Start Prometheus metrics server
        start_http_server(settings.PROMETHEUS_PORT)
        logger.info(f"Prometheus metrics exposed on port {settings.PROMETHEUS_PORT}")
        
        # Start the health check loop
        asyncio.create_task(self.check_system_health())
        logger.info("System health checks are running.")

def main():
    """Main function to run the monitoring system."""
    monitoring = MonitoringSystem()
    monitoring.start()
    
    # Keep the main thread alive
    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring system.")

if __name__ == "__main__":
    # This would be run as a separate service.
    main()