import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ServiceCorreoGmail:
    def __init__(self) -> None:
        self.__smtp_server: str = "smtp.gmail.com"
        self.__port: int = 587

        origen = os.getenv("GMAIL_USER")
        password = os.getenv("GMAIL_PASSWORD")
        destino = os.getenv("EMAIL_ADMIN")

        if not origen or not password or not destino:
            raise ValueError("Variables de entorno de correo no configuradas")
        
        self.__origen_email: str = origen
        self.__password: str = password
        self.__destino_email: str = destino


    def enviar_correo(self, msj: str) -> None:
        msg = self.__prepara_mensaje(msj)

        try:
            with smtplib.SMTP(self.__smtp_server, self.__port) as server:
                server.starttls()
                server.login(self.__origen_email, self.__password)
                server.sendmail(
                    self.__origen_email,
                    self.__destino_email,
                    msg.as_string()
                )
            print("Envío de correo exitoso")

        except smtplib.SMTPException as e:
            print(f" Error al enviar correo: {e}")
            raise

    def __prepara_mensaje(self, msj: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "ACTUALIZACIÓN DEL MODELO"
        msg["From"] = self.__origen_email
        msg["To"] = self.__destino_email

        msg.attach(MIMEText(msj, "plain", "utf-8"))
        return msg
