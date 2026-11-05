"""Simulate alerts - send test alerts to n8n webhook"""

import random
import httpx
import asyncio
from datetime import datetime
from uuid import uuid4


async def send_alert(alert_data: dict, webhook_url: str, webhook_token: str):
    """Send alert to n8n webhook"""
    headers = {"X-Webhook-Token": webhook_token, "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook_url, json=alert_data, headers=headers, timeout=10.0)
            if response.status_code == 200:
                print(f"✅ Alerta enviada: {alert_data['external_id']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error al enviar alerta: {e}")


async def main():
    """Generate and send test alerts"""
    # Configuration
    webhook_url = "http://localhost:5678/webhook/soc-alert"  # Adjust if different
    webhook_token = "dev_webhook_secret_token"  # From .env

    print("🚀 Simulando alertas de seguridad...")
    print(f"📡 Webhook: {webhook_url}")
    print("-" * 60)

    # Alert templates
    alert_templates = [
        {
            "source": "wazuh",
            "rule_id": "5710",
            "rule_description": "sshd: Brute force attack (multiple failed login attempts)",
            "severity_original": "alta",
            "src_ip": f"203.0.113.{random.randint(1, 254)}",
        },
        {
            "source": "wazuh",
            "rule_id": "87105",
            "rule_description": "VirusTotal: Malicious file detected",
            "severity_original": "alta",
            "src_ip": f"192.168.1.{random.randint(1, 254)}",
        },
        {
            "source": "opnsense",
            "rule_id": "31151",
            "rule_description": "Port scan detected from external IP",
            "severity_original": "media",
            "src_ip": f"198.51.100.{random.randint(1, 254)}",
        },
        {
            "source": "wazuh",
            "rule_id": "5502",
            "rule_description": "User login failed",
            "severity_original": "baja",
            "src_ip": f"192.168.1.{random.randint(1, 254)}",
        },
        {
            "source": "wazuh",
            "rule_id": "552",
            "rule_description": "Integrity checksum changed",
            "severity_original": "media",
            "src_ip": f"192.168.1.{random.randint(1, 254)}",
        },
    ]

    # Generate and send alerts
    tasks = []
    for i in range(10):  # Send 10 alerts
        template = random.choice(alert_templates)
        external_id = f"{template['source']}-{uuid4()}"

        alert = {
            "external_id": external_id,
            "source": template["source"],
            "rule_id": template["rule_id"],
            "rule_description": template["rule_description"],
            "severity_original": template["severity_original"],
            "src_ip": template["src_ip"],
            "dst_ip": f"192.168.1.{random.randint(50, 100)}",
            "agent_name": f"server-{random.randint(1, 10)}",
            "raw_payload": {
                "timestamp": datetime.utcnow().isoformat(),
                "original_severity": template["severity_original"],
            },
            "normalized": {
                "rule_id": template["rule_id"],
                "severity": template["severity_original"],
                "description": template["rule_description"],
            },
        }

        tasks.append(send_alert(alert, webhook_url, webhook_token))
        await asyncio.sleep(0.5)  # Delay between alerts

    # Wait for all alerts to be sent
    await asyncio.gather(*tasks)

    print("-" * 60)
    print("✅ Simulación completada")
    print("\n💡 Nota: Si n8n no está configurado, las alertas no se procesarán.")
    print("   Configura el workflow en http://localhost:5678 primero.")


if __name__ == "__main__":
    asyncio.run(main())
