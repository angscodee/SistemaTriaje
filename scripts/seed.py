"""Seed script to populate database with demo data"""

import asyncio
import hashlib
import random
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.core.security import ROLE_PERMISSIONS, hash_password
from app.models import (
    Alert,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)


async def seed_database():
    """Populate database with seed data"""
    print("🌱 Starting database seed...")

    # Create engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Clear existing data (in order due to foreign keys)
        print("Clearing existing data...")
        await session.execute(delete(UserRole))
        await session.execute(delete(RolePermission))
        await session.execute(delete(Alert))
        await session.execute(delete(User))
        await session.execute(delete(Role))
        await session.execute(delete(Permission))
        await session.commit()

        # 1. Create Permissions
        print("Creating permissions...")
        permissions = []
        for perm_name in ROLE_PERMISSIONS["Administrador"]:
            perm = Permission(name=perm_name, description=f"Permiso {perm_name}")
            permissions.append(perm)
            session.add(perm)
        await session.commit()
        print(f"✅ Created {len(permissions)} permissions")

        # 2. Create Roles
        print("Creating roles...")
        roles = {}
        for role_name in ["Administrador", "Analista", "Gestor", "Auditor"]:
            role = Role(name=role_name, description=f"Rol {role_name}")
            session.add(role)
            roles[role_name] = role
        await session.commit()

        # Refresh permissions to get their IDs
        for perm in permissions:
            await session.refresh(perm)

        # 3. Assign permissions to roles
        print("Assigning permissions to roles...")
        perm_dict = {p.name: p for p in permissions}
        for role_name, perm_names in ROLE_PERMISSIONS.items():
            role = roles[role_name]
            for perm_name in perm_names:
                if perm_name in perm_dict:
                    rp = RolePermission(role_id=role.id, permission_id=perm_dict[perm_name].id)
                    session.add(rp)
        await session.commit()
        print("✅ Permissions assigned to roles")

        # 4. Create Users
        print("Creating users...")
        demo_password = hash_password("Demo1234!")
        users_data = [
            ("admin@example.com", "Administrador Sistema", "Administrador"),
            ("analista@example.com", "Analista SOC", "Analista"),
            ("gestor@example.com", "Gestor Ejecutivo", "Gestor"),
            ("auditor@example.com", "Auditor Interno", "Auditor"),
        ]

        for email, full_name, role_name in users_data:
            user = User(
                email=email,
                full_name=full_name,
                password_hash=demo_password,
                is_active=True,
            )
            session.add(user)
            await session.flush()

            # Assign role
            role = roles[role_name]
            user_role = UserRole(user_id=user.id, role_id=role.id)
            session.add(user_role)

        await session.commit()
        print(f"✅ Created {len(users_data)} users")

        # 5. Create Alerts (300+ synthetic alerts)
        print("Creating synthetic alerts...")
        alert_count = 0

        # Alert templates with realistic data
        sources = ["wazuh", "opnsense"]
        rule_templates = [
            ("5710", "sshd: Brute force attack", "alta", ["192.168.1.100", "10.0.0.50"]),
            ("5502", "User login failed", "baja", ["192.168.1.101", "10.0.0.51"]),
            ("552", "Integrity checksum changed", "media", ["192.168.1.102", "10.0.0.52"]),
            ("31100", "Multiple Windows Logon Failures", "media", ["192.168.1.103"]),
            ("87105", "VirusTotal: Malicious file detected", "alta", ["192.168.1.104"]),
            ("31151", "Port scan detected", "media", ["203.0.113.10", "198.51.100.20"]),
        ]

        public_ips = [
            "203.0.113.10",
            "198.51.100.20",
            "192.0.2.30",
            "185.220.101.1",
            "45.155.205.10",
        ]

        # Generate alerts over last 30 days
        now = datetime.utcnow()
        for days_ago in range(30):
            date = now - timedelta(days=days_ago)
            # More alerts in recent days
            alerts_per_day = random.randint(5, 15) if days_ago < 7 else random.randint(2, 8)

            for _ in range(alerts_per_day):
                source = random.choice(sources)
                rule_id, rule_desc, severity_orig, agent_ips = random.choice(rule_templates)
                src_ip = random.choice(public_ips) if random.random() > 0.6 else random.choice(agent_ips)
                dst_ip = random.choice(agent_ips) if src_ip in public_ips else None

                # Calculate fingerprint for deduplication
                ts_rounded = date.replace(second=0, microsecond=0)
                fingerprint_str = f"{source}:{rule_id}:{src_ip}:{dst_ip}:{ts_rounded}"
                fingerprint = hashlib.md5(fingerprint_str.encode()).hexdigest()

                # Determine status based on severity (simulate some already triaged)
                if days_ago > 7:
                    status = random.choice(["triada", "descartada"])
                elif days_ago > 3:
                    status = random.choice(["triada", "pendiente"])
                else:
                    status = "pendiente"

                alert = Alert(
                    external_id=f"{source}-{uuid4()}",
                    source=source,
                    rule_id=rule_id,
                    rule_description=rule_desc,
                    raw_payload={"original": "payload", "timestamp": date.isoformat()},
                    normalized={"rule_id": rule_id, "severity": severity_orig},
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    agent_name=random.choice(agent_ips),
                    severity_original=severity_orig,
                    fingerprint=fingerprint,
                    status=status,
                    received_at=date,
                    triaged_at=date + timedelta(minutes=random.randint(1, 30)) if status == "triada" else None,
                )
                session.add(alert)
                alert_count += 1

        await session.commit()
        print(f"✅ Created {alert_count} synthetic alerts")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("🎉 Database seeded successfully!")
    print("=" * 60)
    print("\nDemo credentials:")
    print("  Administrador: admin@example.com / Demo1234!")
    print("  Analista:      analista@example.com / Demo1234!")
    print("  Gestor:        gestor@example.com / Demo1234!")
    print("  Auditor:       auditor@example.com / Demo1234!")
    print("\nAccess the dashboard at: http://localhost")
    print("Access the API docs at: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())
