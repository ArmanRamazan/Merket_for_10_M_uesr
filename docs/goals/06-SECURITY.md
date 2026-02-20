# 06 — Безопасность и Compliance

> Владелец: Architect / Security Lead
> Последнее обновление: 2026-02-19

---

## Модель угроз (Top-level)

| Угроза | Вероятность | Импакт | Митигация |
|--------|------------|--------|-----------|
| SQL Injection / XSS | Высокая | Критический | ORM, parameterized queries, CSP headers |
| Account takeover | Высокая | Критический | 2FA, rate limiting, anomaly detection |
| Payment fraud | Высокая | Критический | 3DS, fraud scoring, escrow |
| DDoS | Средняя | Высокий | CDN, rate limiting, auto-scaling |
| Data breach | Средняя | Критический | Encryption at rest/transit, access control |
| Fake teachers/courses | Высокая | Высокий | Verification, AI moderation, manual review |
| Insider threat | Низкая | Критический | RBAC, audit logs, principle of least privilege |

---

## TODO: Security Architecture

### Application Security
- [ ] 🔴 Определить authentication flow: OAuth2 + JWT, token rotation, device fingerprinting
- [ ] 🔴 API Gateway: rate limiting per user/IP, request validation, CORS policy
- [ ] 🔴 Input validation стратегия: whitelist approach, sanitization на каждом уровне
- [ ] 🔴 Secrets management: Vault / AWS Secrets Manager, rotation policy
- [ ] 🔴 Dependency scanning: автоматическая проверка уязвимостей в зависимостях (CI)

### Infrastructure Security
- [ ] 🔴 Network segmentation: public / private / data subnets
- [ ] 🔴 mTLS между сервисами (service mesh или manual)
- [ ] 🔴 Database access: только через сервисы, никогда напрямую, connection через VPN
- [ ] 🔴 Container security: non-root, read-only filesystem, minimal base images
- [ ] 🔴 Kubernetes RBAC: service accounts с минимальными правами

### Payment Security
- [ ] 🔴 PCI DSS Level 1 compliance roadmap (при > $6M транзакций/год)
- [ ] 🔴 Card tokenization: никогда не хранить PAN, только токены от провайдера
- [ ] 🔴 Fraud detection rules: velocity checks, geo-mismatch, amount anomalies
- [ ] 🔴 3D Secure для транзакций > порога

### Data Protection
- [ ] 🔴 Encryption at rest: AES-256 для БД, S3 server-side encryption
- [ ] 🔴 Encryption in transit: TLS 1.3 everywhere, certificate management
- [ ] 🔴 PII handling: классификация данных, маскирование в логах
- [ ] 🔴 Backup encryption и secure storage

### Monitoring и Incident Response
- [ ] 🔴 Security event logging: auth events, permission changes, data access
- [ ] 🔴 SIEM стратегия: агрегация security logs, correlation rules
- [ ] 🔴 Incident response playbook: detection → containment → eradication → recovery
- [ ] 🔴 Bug bounty program (Phase 2+)

### Compliance
- [ ] 🔴 Определить applicable regulations по целевым рынкам
- [ ] 🔴 Privacy policy и Terms of Service — юридический ревью
- [ ] 🔴 Cookie consent и tracking compliance
- [ ] 🔴 Data Processing Agreement для sub-processors
