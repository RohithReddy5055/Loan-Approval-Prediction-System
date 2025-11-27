"""
Email service for sending notifications via SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import os

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.environ.get('SMTP_USE_TLS', 'True').lower() == 'true'
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_username)
        self.from_name = os.environ.get('FROM_NAME', 'Loan Application System')
        
        # Check if SMTP is configured
        self.enabled = bool(self.smtp_username and self.smtp_password)
        
        if not self.enabled:
            logger.warning("SMTP not configured. Email notifications will be disabled.")
            logger.info("To enable SMTP, set environment variables: SMTP_USERNAME, SMTP_PASSWORD")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional, auto-generated from HTML if not provided)
            attachments: List of file paths to attach (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email not sent to {to_email}: SMTP not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create plain text version if not provided
            if not body_text:
                # Simple HTML to text conversion
                import re
                body_text = re.sub(r'<[^>]+>', '', body_html)
                body_text = body_text.replace('&nbsp;', ' ')
            
            # Add body parts
            part1 = MIMEText(body_text, 'plain')
            part2 = MIMEText(body_html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_application_confirmation(
        self,
        to_email: str,
        applicant_name: str,
        application_id: str,
        loan_type: str,
        loan_amount: float,
        emi_info: Optional[dict] = None
    ) -> bool:
        """
        Send loan application confirmation email.
        
        Args:
            to_email: Applicant email address
            applicant_name: Applicant name
            application_id: Application ID
            loan_type: Type of loan
            loan_amount: Loan amount requested
            emi_info: EMI information dictionary (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        loan_type_names = {
            'education': 'Education Loan',
            'home': 'Home Loan',
            'car': 'Car Loan',
            'personal': 'Personal Loan',
            'business': 'Business Loan'
        }
        
        loan_type_display = loan_type_names.get(loan_type, loan_type.title())
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
                .emi-box {{ background: #e8f5e9; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Application Received</h1>
                    <p>Thank you for applying with us!</p>
                </div>
                <div class="content">
                    <p>Dear {applicant_name},</p>
                    
                    <p>We have successfully received your <strong>{loan_type_display}</strong> application. Our team will review your application and get back to you soon.</p>
                    
                    <div class="info-box">
                        <h3 style="margin-top: 0;">Application Details</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Loan Type:</strong> {loan_type_display}</p>
                        <p><strong>Loan Amount:</strong> ₹{loan_amount:,.0f}</p>
                    </div>
                    
                    {f'''
                    <div class="emi-box">
                        <h4 style="margin-top: 0;">Estimated EMI Information</h4>
                        <p><strong>Monthly EMI:</strong> ₹{emi_info.get('emi', 0):,.2f}</p>
                        <p><strong>Interest Rate:</strong> {emi_info.get('interest_rate', 0)}% p.a.</p>
                        <p><strong>Total Amount:</strong> ₹{emi_info.get('total_amount', 0):,.2f}</p>
                    </div>
                    ''' if emi_info and emi_info.get('emi') else ''}
                    
                    <p>You can track your application status using your Application ID: <strong>{application_id}</strong></p>
                    
                    <p>If you have any questions, please feel free to contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>Loan Application System</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"Loan Application Confirmation - {application_id[:8]}"
        
        return self.send_email(to_email, subject, html_body)
    
    def send_status_update(
        self,
        to_email: str,
        applicant_name: str,
        application_id: str,
        loan_type: str,
        status: str,
        remarks: Optional[str] = None,
        approval_reason: Optional[str] = None
    ) -> bool:
        """
        Send application status update email.
        
        Args:
            to_email: Applicant email address
            applicant_name: Applicant name
            application_id: Application ID
            loan_type: Type of loan
            status: New status (approved/rejected/pending)
            remarks: Additional remarks (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        loan_type_names = {
            'education': 'Education Loan',
            'home': 'Home Loan',
            'car': 'Car Loan',
            'personal': 'Personal Loan',
            'business': 'Business Loan'
        }
        
        loan_type_display = loan_type_names.get(loan_type, loan_type.title())
        
        status_info = {
            'approved': {
                'title': '🎉 Application Approved!',
                'color': '#4caf50',
                'message': 'Congratulations! Your loan application has been approved.'
            },
            'rejected': {
                'title': 'Application Status Update',
                'color': '#f44336',
                'message': 'We regret to inform you that your loan application has been rejected.'
            },
            'pending': {
                'title': 'Application Under Review',
                'color': '#ff9800',
                'message': 'Your application is currently under review.'
            }
        }
        
        info = status_info.get(status.lower(), status_info['pending'])
        
        # Build approval/rejection details section
        details_section = ""
        if approval_reason or remarks:
            bg_color = '#e8f5e9' if status.lower() == 'approved' else '#ffebee'
            title = '✓ Approval Details' if status.lower() == 'approved' else '✗ Rejection Details'
            reason_text = approval_reason or remarks or 'No additional details provided.'
            
            details_section = f"""
                    <div class="info-box" style="background: {bg_color}; border-left-color: {info['color']};">
                        <h3 style="margin-top: 0; color: {info['color']};">{title}</h3>
                        <p style="white-space: pre-line; line-height: 1.8;"><strong>Reason:</strong><br>{reason_text}</p>
                    </div>
            """
        
        # Build additional remarks section if both approval_reason and remarks exist
        remarks_section = ""
        if remarks and approval_reason:
            remarks_section = f"""
                    <div class="info-box">
                        <p><strong>Additional Remarks:</strong> {remarks}</p>
                    </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {info['color']}; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid {info['color']}; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{info['title']}</h1>
                </div>
                <div class="content">
                    <p>Dear {applicant_name},</p>
                    
                    <p>{info['message']}</p>
                    
                    <div class="info-box">
                        <h3 style="margin-top: 0;">Application Details</h3>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Loan Type:</strong> {loan_type_display}</p>
                        <p><strong>Status:</strong> <span style="color: {info['color']}; font-weight: bold;">{status.upper()}</span></p>
                    </div>
                    
                    {details_section}
                    {remarks_section}
                    
                    <p>If you have any questions, please feel free to contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>Loan Application System</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"Loan Application Status Update - {status.upper()}"
        
        return self.send_email(to_email, subject, html_body)


# Global email service instance
email_service = EmailService()

