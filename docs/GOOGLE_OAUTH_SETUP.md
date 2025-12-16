# Google OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name: `TeamAI` (or your choice)
4. Click **"Create"**

## Step 2: Enable Google OAuth2 API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"** or **"People API"**
3. Click **"Enable"**

## Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Choose **"External"** (for testing) or **"Internal"** (if you have Google Workspace)
3. Fill in:
   - **App name**: TeamAI
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **"Save and Continue"**
5. **Scopes**: Click **"Add or Remove Scopes"**, select:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
6. Click **"Save and Continue"**
7. **Test users** (if External): Add your Gmail address
8. Click **"Save and Continue"** → **"Back to Dashboard"**

## Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. **Application type**: Web application
4. **Name**: TeamAI Local Dev
5. **Authorized JavaScript origins**:
   ```
   http://localhost:8000
   http://localhost:3000
   ```
6. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   ```
7. Click **"Create"**
8. **Copy** the Client ID and Client Secret (you'll need these!)

## Step 5: Update Backend Configuration

1. Open `/workspaces/TeamAI/backend/.env`
2. Replace the empty values:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

## Step 6: Restart Backend

```bash
cd /workspaces/TeamAI
docker-compose restart backend
```

## Step 7: Test OAuth Flow

1. Open http://localhost:3000/login
2. Click **"Sign in with Google"**
3. You should be redirected to Google login
4. After authenticating, you'll be redirected back to the dashboard

## Troubleshooting

### Error: "redirect_uri_mismatch"
- **Fix**: Make sure the redirect URI in Google Console exactly matches:
  ```
  http://localhost:8000/api/v1/auth/google/callback
  ```
  (No trailing slash, exact protocol `http://`)

### Error: "Access blocked: This app's request is invalid"
- **Fix**: You forgot to add your email as a test user in the OAuth consent screen

### Error: "invalid_client"
- **Fix**: Double-check your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `backend/.env`

### Login button doesn't redirect
- **Fix**: Check backend logs: `docker-compose logs backend | tail -20`
- Verify `GOOGLE_CLIENT_ID` is not empty

## Optional: Restrict to Google Workspace Domain

If you want to restrict login to only your company's Google Workspace:

1. In `backend/.env`, set:
   ```bash
   GOOGLE_WORKSPACE_DOMAIN=yourcompany.com
   ```

2. Restart backend:
   ```bash
   docker-compose restart backend
   ```

Now only users with `@yourcompany.com` emails can sign in.

## Next Steps

Once Google OAuth is working:
- ✅ Users can sign in with their Google accounts
- ✅ JWT tokens are issued after successful authentication
- ✅ Role-based access control works (admin vs team_user)
- ✅ Invites can be sent to new users

Continue with Phase 2: Marketplace UI!
