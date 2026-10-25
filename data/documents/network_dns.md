\# DNS Troubleshooting



\## Problem



An application may fail to connect to a service when the hostname

cannot be resolved to the expected IP address.



\## Symptoms



\- Hostname cannot be resolved.

\- Application reports an unknown host error.

\- Connection works when using an IP address but fails when using

&#x20; a hostname.

\- DNS resolution returns an unexpected address.



\## Investigation Steps



\### Step 1: Verify the Hostname



Confirm that the configured hostname is correct.



\### Step 2: Test DNS Resolution



Use an approved DNS lookup tool to verify whether the hostname

resolves correctly.



\### Step 3: Compare the Resolved Address



Verify that the resolved IP address matches the expected server.



\### Step 4: Check DNS Configuration



Verify the configured DNS servers and relevant DNS records.



\## Resolution



Correct the hostname or DNS configuration when an incorrect

DNS record or configuration is identified.



\## Warning



Do not modify production DNS records without following

approved change procedures.

