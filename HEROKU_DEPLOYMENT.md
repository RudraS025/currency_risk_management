# Heroku Deployment Configuration

## Environment Variables Required

Set these environment variables in your Heroku app:

```bash
# Required for web application
SECRET_KEY=your-secret-key-here-generate-random-string
FLASK_ENV=production

# Optional: External API keys for enhanced functionality
EXCHANGERATE_API_KEY=your-exchangerate-api-key
FIXER_API_KEY=your-fixer-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
```

## Heroku CLI Commands

1. **Install Heroku CLI**: Download from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

4. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set FLASK_ENV=production
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Open App**:
   ```bash
   heroku open
   ```

## Optional: Set up Daily Scheduler

To enable daily automated updates:

```bash
heroku addons:create scheduler:standard
heroku addons:open scheduler
```

Add job: `python -m examples.daily_update_scheduler`
Set frequency: Daily at 9:00 AM UTC

## Monitoring

Check app logs:
```bash
heroku logs --tail
```

Check app status:
```bash
heroku ps
```
