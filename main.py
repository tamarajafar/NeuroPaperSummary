[secrets]
OPENAI_API_KEY = "your_openai_api_key"
EMAIL_USERNAME = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"

[firebase]
credentials = '''
{
    "type": "service_account",
    "project_id": "personalwebapp-5c548",
    "private_key_id": "your_private_key_id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
    "client_email": "firebase-adminsdk-fbsvc@personalwebapp-5c548.iam.gserviceaccount.com",
    "client_id": "116158642168732013953",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40personalwebapp-5c548.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
'''
