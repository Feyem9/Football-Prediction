import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Envoie un email via SMTP.
    
    En développement (MailDev): pas d'authentification, pas de TLS
    En production: authentification + TLS
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.from_email
        message["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            # TLS et auth seulement en production
            if settings.smtp_use_tls:
                server.starttls()
            
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            
            server.sendmail(settings.from_email, to_email, message.as_string())
        
        print(f"✅ Email envoyé à {to_email}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False



async def send_reset_password_email(email: str, reset_token: str) -> bool:
    """
    Envoie un email de réinitialisation de mot de passe.
    
    Args:
        email: Email du destinataire
        reset_token: Token de réinitialisation
        
    Returns:
        True si envoyé, False sinon
    """
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #4CAF50; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin: 20px 0;
            }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔐 Réinitialisation de mot de passe</h2>
            <p>Bonjour,</p>
            <p>Vous avez demandé à réinitialiser votre mot de passe sur {settings.app_name}.</p>
            <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
            <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
            <p>Ou copiez ce lien dans votre navigateur :</p>
            <p><code>{reset_url}</code></p>
            <p><strong>Ce lien expire dans {settings.password_reset_expire_hours} heure(s).</strong></p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
            <div class="footer">
                <p>— L'équipe {settings.app_name}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, f"🔐 {settings.app_name} - Réinitialisation de mot de passe", html_content)


async def send_verification_email(email: str, verification_token: str) -> bool:
    """
    Envoie un email de vérification d'adresse email.
    
    Args:
        email: Email du destinataire
        verification_token: Token de vérification
        
    Returns:
        True si envoyé, False sinon
    """
    verify_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #2196F3; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin: 20px 0;
            }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✉️ Confirmez votre adresse email</h2>
            <p>Bonjour,</p>
            <p>Merci de vous être inscrit sur {settings.app_name} !</p>
            <p>Pour activer votre compte, veuillez confirmer votre adresse email :</p>
            <a href="{verify_url}" class="button">Confirmer mon email</a>
            <p>Ou copiez ce lien dans votre navigateur :</p>
            <p><code>{verify_url}</code></p>
            <p>Si vous n'avez pas créé de compte, ignorez cet email.</p>
            <div class="footer">
                <p>— L'équipe {settings.app_name}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, f"✉️ {settings.app_name} - Confirmez votre email", html_content)
