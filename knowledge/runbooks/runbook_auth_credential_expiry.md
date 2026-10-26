# RB-AUTH-004: Remediation for Expired Authentication Signing Keys

## Summary
Guidance for resolving widespread authentication rejections, 401 Unauthorized errors, and token verification failures resulting from expired JWT public keys, OAuth certificates, or LDAP service account passwords.

## Symptoms
- Influx of HTTP 401 and 403 status codes in `auth-service` logs.
- Log messages stating: `JWTExpiredError: signature has expired`, `InvalidTokenSignature: key rotated without cache update`, or `LDAPBindError: InvalidCredentials`.
- User login success rate drops below 10%.

## Verification Steps
1. Query `log_entries` for `auth-service` searching for `signature has expired` or `certificate expired`.
2. Inspect `metric_samples` for `auth_failure_rate` and `login_requests`.
3. Check certificate expiration metadata or key rotation timestamps.

## Remediation Protocol
- **Action:** Propose `refresh_service_credentials` (Simulated rotation and cache flush).
- **Risk Level:** HIGH. This action triggers credential cache invalidation across all authenticating nodes.
- **Approval Requirement:** Requires explicit sign-off from Incident Commander or Security Lead.
- **Verification:** Once executed, verify that authentication error rate returns to 0% and test tokens issue successfully.
