# Security & Secrets

- **DSU keys (dev):** checked out locally in `/secrets/dev_keys` (NEVER commit).
- **Prod keys:** HSM only; access via short-lived tokens; 3-of-4 quorum enforced in DSU.
- **Secrets:** use Doppler/Vault/KMS; never .env in prod.
- **PII:** none expected; flag any addition to Model Risk immediately.
- **SBOM:** generate at build; fail CI on critical CVEs.