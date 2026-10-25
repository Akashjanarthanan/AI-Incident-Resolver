# Oracle Connectivity Troubleshooting

## Problem

An application may be unable to establish a connection with an
Oracle database because of listener, network, port, firewall,
or configuration issues.

## Common Checks

1. Verify the database hostname.
2. Verify the Oracle listener is running.
3. Verify the configured listener port.
4. Test network connectivity from the application server.
5. Verify firewall rules.
6. Verify the application's database connection configuration.

## Port

The default Oracle listener port is commonly 1521.

## Troubleshooting Logic

If the database host cannot be reached:

Investigate network connectivity.

If the host is reachable but the listener port is unavailable:

Investigate listener status or firewall configuration.

If the listener is available but the application still cannot
connect:

Investigate application connection configuration and credentials.

## Resolution Principle

Troubleshooting should proceed from basic connectivity checks
toward application-level configuration checks.