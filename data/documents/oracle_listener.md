# Oracle Listener Troubleshooting

## Problem

Applications may fail to connect to an Oracle database when the
Oracle listener is unavailable or the listener is not accepting
connections.

A common error associated with this situation is:

ORA-12541: TNS:no listener

## Symptoms

- Application cannot connect to Oracle database.
- Database connection timeout may occur.
- Users may receive ORA-12541.
- Database host may still be reachable.

## Investigation Steps

### Step 1: Check Listener Status

Run:

lsnrctl status

Verify whether the Oracle listener is running.

### Step 2: Check Listener Port

The default Oracle listener port is commonly:

1521

Verify that the listener is configured to use the expected port.

### Step 3: Check Network Connectivity

Verify that the application server can reach the database server
on the configured listener port.

### Step 4: Check Firewall

Verify that firewall rules are not blocking communication between
the application server and database server.

## Resolution

If the listener is stopped and the environment allows restarting
the service, start the listener using:

lsnrctl start

After starting the listener, verify its status again:

lsnrctl status

## Important Note

Do not restart production services without following the
organization's change-management and approval procedures.