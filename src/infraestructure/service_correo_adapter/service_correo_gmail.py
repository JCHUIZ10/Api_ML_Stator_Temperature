import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from aplication.service.serice_correo_port import IServicioCorreo

class ServiceCorreoGmail(IServicioCorreo):
    __smtp_server:str
    __password:str
    __port:int
    __origen_email:str
    __destino_email:str

    def __init__(self)->None:
        self.__smtp_server = "smtp.gmail.com"
        self.__password = "otiq ctew pyhw uddf"
        self.__port= 587
        self.__origen_email= "escorpioyvirgo18@gmail.com"
        self.__destino_email= "ciferbeach@gmail.com"
        

    def enviar_correo(self) -> None:
        #Preparamos el mensaje(Creamos el Objeto)
        msg = self.__prepara_mensaje()

        #Realizamos el modelo
        with smtplib.SMTP(self.__smtp_server, self.__port) as server:
            server.starttls()
            server.login(self.__origen_email, self.__password)
            server.sendmail(self.__origen_email, self.__destino_email, msg.as_string())
        print("Envio Exitoso")


    def __prepara_mensaje(self) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "ACTUALIZACION DEL MODELO"
        msg["From"] = self.__origen_email
        msg["To"] = self.__destino_email

        texto = "Se acaba de actualizar el modelo"
        msg.attach(MIMEText(texto, "plain"))
        return msg