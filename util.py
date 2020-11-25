import getpass
from hashlib import sha256
from os import path, mkdir, listdir
from re import search
import smtplib
from email.mime.text import MIMEText
from email.parser import Parser


def search_string(regex, string):
    return search(regex, string)


def hash_password(password):
    return sha256(password.encode()).hexdigest()


def input_password():
    return getpass.getpass("Mot de passe: ")


def check_file_exists(path_file):
    return path.exists(path_file)


def create_directory(name):
    mkdir(name)


def send_mail(sender, recipient, message):
    smtpConnection = smtplib.SMTP(host="smtp.ulaval.ca", timeout=10)
    smtpConnection.sendmail(sender, recipient, message.as_string())
    smtpConnection.quit()


def get_message_MIME(sender, recipient, subject, message):
    msg = MIMEText(message)
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    return msg


def get_number_files_directory(directory):
    return len([name for name in listdir(directory)])


def get_directory_size(directory):
    files = get_files_directory(directory)
    size = 0
    for file in files:
        size += path.getsize(file)
    return size


def get_files_directory(directory):
    fileList = [f"{directory}{name}" for name in listdir(directory)]
    fileList.sort()
    return fileList


def create_MIME_File(file_path):
    with open(file_path, "r") as file:
        return Parser().parse(file)


def getSubjectOfMail(msg):
    return msg["Subject"]
