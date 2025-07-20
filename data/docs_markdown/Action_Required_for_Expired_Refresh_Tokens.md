# Action Required for Expired Refresh Tokens
May 2025
We’ve identified that some suppliers who generated their refresh tokens before we switched to non-expiring tokens may encounter token expiration after 365 days. This can lead to worker downtime and authentication errors such as:
JSON
```
{"error":"invalid_grant", "error_description":"Unknown or invalid refresh token."}

```

**Error:**  
_Authentication failed. Your token might be invalid or expired. Please re-generate one and try again. Use  
`--no_cache=true` flag to re-authenticate._
To resolve this, please follow these steps to generate a new **non-expiring** refresh token and restart your worker:
**Step 1:**  
Run the `io.net worker` CLI binary with the `--no_cache=true` flag to initiate token regeneration.
**Step 2:**  
Provide any required details to the CLI. Once successful, your worker will launch using the refreshed token.
> ## 📘
> After completing the initial interactive authentication, you’ll see a new --token value. You can reuse this token to update other devices silently.
Thank you for your continued support of io.net.  
The io.net Team
about 2 months ago
* * *
