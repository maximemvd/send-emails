import socket
import optparse
import sys
import util


def get_parser():
    parser = optparse.OptionParser()
    parser.add_option( "-p", "--port", dest="port", type=int, default=1400,
                       help="Port pour écouter et envoyer des messages" )
    return parser.parse_args( sys.argv[1:] )[0]


def show_login_menu():
    print( "Menu de connexion\n" )
    print( "1. Creer un compte\n" )
    print( "2. Se connecter" )


def show_main_menu():
    print( "Menu principal\n" )
    print( "1. Consultation de courriels\n" )
    print( "2. Envoi de courriel\n" )
    print( "3. Statistiques\n" )
    print( "4. Quitter" )


def get_username():
    return input( "Nom d'utilisateur :" )


def get_password():
    return util.input_password()


def check_login_answer(login_answer):
    return login_answer == "1" or login_answer == "2"


def get_account_infos():
    username = get_username()
    password = get_password()
    return username, password


def create_account():
    username, password = get_account_infos()
    infos = {"command": "signup", "username": username, "password": password}
    message = str(infos)
    send_message_to_server(message)
    return username


def login():
    username, password = get_account_infos()
    infos = {"command": "login", "username": username, "password": password}
    message = str(infos)
    send_message_to_server(message)
    return username

def get_login_command():
    command_successful = False
    while not command_successful:
        show_login_menu()
        login_command = input()
        command_successful = check_login_answer(login_command)
        if not command_successful:
            print("La commande entree n'est pas valide, Entrer un nombre de 1 à 2")
    return login_command


def check_main_menu_command(main_menu_command):
    choix = {"1", "2", "3", "4"}
    return main_menu_command in choix


def get_main_menu_command():
    command_successful = False
    while not command_successful:
        show_main_menu()
        main_menu_command = input()
        command_successful = check_main_menu_command(main_menu_command)
        if not command_successful:
            print("La commande entree n'est pas valide. Entrer un nombre de 1 a 4")
    return main_menu_command


def create_socket():
    port = get_parser().port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", port))
    return client_socket

def receive_message_from_server():
    message = CLIENT_SOCKET.recv(2048).decode()
    return message

def send_message_to_server(message):
    CLIENT_SOCKET.send(message.encode())












