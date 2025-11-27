# SMTP Email Configuration Guide

This guide explains how to configure SMTP email notifications for the Loan Application System.

## Overview

The system can send automated email notifications for:
- Application confirmation emails when a loan application is submitted
- Status update emails when application status changes (approved/rejected)

## Configuration

### Method 1: Environment Variables (Recommended)

Set the following environment variables:

```bash
# SMTP Server Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True

# SMTP Authentication
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email Sender Information
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Loan Application System
```

### Method 2: .env File

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your SMTP credentials

3. Install python-dotenv (if not already installed):
   ```bash
   pip install python-dotenv
   ```

4. Update `app.py` to load environment variables from `.env`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## Gmail Setup

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Enable 2-Step Verification

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Loan Application System" as the name
4. Click "Generate"
5. Copy the 16-character password (use this as `SMTP_PASSWORD`)

### Step 3: Configure Environment Variables
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Your 16-character app password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Loan Application System
```

## Other Email Providers

### Outlook/Hotmail
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Yahoo Mail
```bash
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

### Custom SMTP Server
```bash
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@yourdomain.com
SMTP_PASSWORD=your-password
```

## Testing Email Configuration

You can test your SMTP configuration by:

1. Submitting a loan application - you should receive a confirmation email
2. Checking server logs for email sending status
3. Using the Python shell:
   ```python
   from utils.email_service import email_service
   
   # Test email
   email_service.send_email(
       to_email='test@example.com',
       subject='Test Email',
       body_html='<h1>Test</h1><p>This is a test email.</p>'
   )
   ```

## Troubleshooting

### Email not sending
1. Check that all environment variables are set correctly
2. Verify SMTP credentials are correct
3. Check server logs for error messages
4. Ensure firewall allows SMTP connections
5. For Gmail, make sure you're using an App Password, not your regular password

### Authentication Errors
- Gmail: Use App Password, not regular password
- Enable "Less secure app access" (not recommended) or use App Password (recommended)
- Check that 2FA is enabled if using Gmail

### Connection Errors
- Verify SMTP_HOST and SMTP_PORT are correct
- Check firewall settings
- Try different ports (587 for TLS, 465 for SSL)

## Security Notes

- Never commit `.env` file to version control
- Use App Passwords instead of regular passwords when possible
- Keep SMTP credentials secure
- Consider using environment variables in production instead of `.env` files

## Disabling Email Notifications

If you don't want to use email notifications, simply don't set the `SMTP_USERNAME` and `SMTP_PASSWORD` environment variables. The system will continue to work without sending emails, and will log warnings instead.

