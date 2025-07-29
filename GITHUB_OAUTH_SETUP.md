# GitHub OAuth Setup for Grafana

## Step 1: Create GitHub OAuth App

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: `Netflix Network Telemetry Grafana`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/login/github`

## Step 2: Get OAuth Credentials

After creating the OAuth app, you'll get:
- **Client ID**: Copy this value
- **Client Secret**: Click "Generate a new client secret" and copy the value

## Step 3: Update Environment Variables

Replace the placeholder values in `docker-compose.yml`:

```yaml
- GF_AUTH_GITHUB_CLIENT_ID=your_actual_client_id
- GF_AUTH_GITHUB_CLIENT_SECRET=your_actual_client_secret
```

## Step 4: Optional Team/Org Restrictions

If you want to restrict access to specific teams or organizations:

```yaml
- GF_AUTH_GITHUB_TEAM_IDS=team_id_1,team_id_2
- GF_AUTH_GITHUB_ALLOWED_ORGANIZATIONS=your_org_name
```

## Step 5: Restart Containers

```bash
docker compose down
docker compose up -d
```

## Step 6: Test OAuth

1. Go to `http://localhost:3000`
2. Click "Sign in with GitHub"
3. Authorize the application
4. You should be redirected back to Grafana

## Troubleshooting

- Make sure the callback URL matches exactly
- Check Grafana logs: `docker compose logs grafana`
- Verify OAuth app settings in GitHub
- Ensure the client secret is correct