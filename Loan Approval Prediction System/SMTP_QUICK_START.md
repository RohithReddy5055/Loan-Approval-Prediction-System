# SMTP Quick Start Guide

## ✅ Step-by-Step Setup

### 1. **Create/Edit Your `.env` File**

Create a `.env` file in your project root (same folder as `app.py`) with the following content:

```env
# SMTP Server Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True

# SMTP Authentication (REQUIRED)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here

# Email Sender Information
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Loan Application System
```

### 2. **Get Gmail App Password (If Using Gmail)**

**For Gmail users, you MUST use an App Password, not your regular password:**

1. **Enable 2-Step Verification** (if not already enabled):
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Loan Application System"
   - Click "Generate"
   - Copy the 16-character password (it looks like: `abcd efgh ijkl mnop`)
   - **Use this as your `SMTP_PASSWORD`** (remove spaces or keep them, both work)

### 3. **Fill in Your `.env` File**

Replace the placeholder values:
- `SMTP_USERNAME`: Your Gmail address (e.g., `youremail@gmail.com`)
- `SMTP_PASSWORD`: Your 16-character App Password from step 2
- `FROM_EMAIL`: Same as SMTP_USERNAME
- `FROM_NAME`: Can be anything (e.g., "Loan Application System")

**Example `.env` file:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=john.doe@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=john.doe@gmail.com
FROM_NAME=Loan Application System
```

### 4. **Install python-dotenv (If Not Already Installed)**

```bash
pip install python-dotenv
```

### 5. **Restart Your Flask Server**

**IMPORTANT:** After creating/editing your `.env` file, you MUST restart your Flask server for changes to take effect.

```bash
# Stop your current server (Ctrl+C)
# Then restart:
python app.py
```

### 6. **Test Your SMTP Configuration**

#### Option A: Submit a Test Loan Application
1. Go to your application form (e.g., `/apply/education-loan`)
2. Fill out and submit a test application
3. Check your email inbox for the confirmation email
4. Check server logs for any error messages

#### Option B: Test via Python Shell
```python
from utils.email_service import email_service

# Test email
result = email_service.send_email(
    to_email='your-test-email@gmail.com',
    subject='Test Email from Loan System',
    body_html='<h1>Test</h1><p>This is a test email from the Loan Application System.</p>'
)

if result:
    print("✅ Email sent successfully!")
else:
    print("❌ Email failed to send. Check server logs.")
```

## 🔍 Troubleshooting

### ❌ "SMTP not configured" Warning
- **Solution**: Make sure your `.env` file exists and has `SMTP_USERNAME` and `SMTP_PASSWORD` set
- **Check**: Restart your Flask server after creating `.env`

### ❌ "SMTP authentication failed"
- **Gmail**: Make sure you're using an **App Password**, not your regular password
- **Check**: Verify 2-Step Verification is enabled
- **Check**: Make sure there are no extra spaces in your password

### ❌ "Connection refused" or "Connection timeout"
- **Check**: Verify `SMTP_HOST` and `SMTP_PORT` are correct
- **Gmail**: Should be `smtp.gmail.com` and `587`
- **Check**: Firewall/antivirus might be blocking SMTP connections

### ❌ Email not received
- **Check**: Check spam/junk folder
- **Check**: Verify recipient email address is correct
- **Check**: Look at server logs for error messages

## 📧 Other Email Providers

### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
```

### Yahoo Mail
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@yahoo.com
```

## ✅ Verification Checklist

- [ ] `.env` file created in project root
- [ ] `SMTP_USERNAME` filled in
- [ ] `SMTP_PASSWORD` filled in (App Password for Gmail)
- [ ] `FROM_EMAIL` filled in
- [ ] `python-dotenv` installed (`pip install python-dotenv`)
- [ ] Flask server restarted after creating `.env`
- [ ] Test email sent successfully

## 🎯 What Happens When SMTP is Configured

Once SMTP is properly configured, the system will automatically:
1. ✅ Send confirmation emails when loan applications are submitted
2. ✅ Send status update emails when applications are approved/rejected
3. ✅ Log email sending status in server logs

If SMTP is not configured, the system will still work but emails won't be sent (you'll see warnings in logs).

