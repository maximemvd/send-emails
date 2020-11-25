import socket
import optparse
import sys
import util


def get_parser():
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", dest="port", type=int, default=1400,
                       help="Port pour écouter et envoyer des messages")
    return parser.parse_args(sys.argv[1:])[0]


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


def get_mails(username):
    data = {"command" : "check_mails", "username" : username}
    send_message_to_server(str(data))

    server_response = eval(receive_message_from_server())
    if not server_response.get("status"):
        print("\n" + server_response.get("message"))
        return False
    return server_response.get("mail_list")


def show_mail(content):
    for key in content:
        print(content.get(key))


def show_inbox(mails, nb_mail):
    print(f"\nVotre boite de reception contient {nb_mail} messages : ")
    for i in range(1, nb_mail + 1):
        subject = mails.get(i).get("subject")
        print(f"{i} - {subject[8:]}")

def show_mails(mails):
    nb_mails = len(mails)
    while True:
        show_inbox(mails, nb_mails)
        mail_number = input("\nEntrer le numéro du courriel que vous désirez consulter")
        try:
            mail_number = int(mail_number)
        except:
            print("Veuillez entrer un nombre valide")
        else:
            if mail_number > nb_mails or mail_number < 0:
                print(f"Veuillez entrer un numero entre 1 et {nb_mails}")
                continue
            print()
            show_mail(mails.get(mail_number))
            print("\n Désirez-vous consulter un autre courriel? (Oui/Non)")
            command = input()
            if command.lower() == "non":
                break

def check_mails(username):
    mails = get_mails(username)
    if not mails:
        return
    show_mails(mails)


def send_mail(username):
    recipient = input("Indiquer l'adresse de destination : ")
    subject = input("Objet de votre message : ")
    print("Message : ")
    message = input("")
    data = {"command" : "send_mail", "sender" : username, "recipient" : recipient, "subject" : subject, "body" : message}

    print("\nLe message est en train d'envoyer")
    send_message_to_server(str(data))



def get_stats(username):
    data = {"command" : "check_stats", "username" : username}
    send_message_to_server((str(data)))
    reponse_serveur = eval(receive_message_from_server())
    return reponse_serveur

def show_stats(stats):
    username = stats.get( "username" )
    nb_mails = stats.get( "nb_mails" )
    directory_size = stats.get( "directory_size" )
    mail_list = stats.get( "mail_list" )

    print( '\n' + f"--------- Information de l'utilisateur {username} ---------\n" )
    print( f"Vous avez {nb_mails} courriel(s)." )
    print( f"La taille totale de la boite de courriels est de {directory_size} octets." )
    print( "Voici la liste des courriels:")
    for i in range(1, len(mail_list) + 1):
        subject = mail_list.get(i)
        print(f"{i} - {subject}")

    input("\nAppuyer sur Enter pour aller au menu")


def check_stats(username):
    stats = get_stats(username)
    show_stats(stats)


def endConnection():
    data = {"command": "quit"}
    send_message_to_server(str(data))
    quit()


def main():
    username = ""
    while_login = True
    while while_login:
        login_command = get_login_command()
        if login_command == "1":
            username = create_account()

        elif login_command == "2":
            username = login()

        reponse_serveur = eval(receive_message_from_server())
        print('\n' + reponse_serveur.get("message"))
        while_login = not reponse_serveur.get("status")

    while True:
        menu_command = get_main_menu_command()
        if menu_command == "1":
            check_mails(username)
            continue

        elif menu_command == "2":
            send_mail(username)

        elif menu_command == "3":
            check_stats(username)
            continue

        elif menu_command == "4":
            endConnection()

        reponse_serveur = eval(receive_message_from_server())
        print('\n' + reponse_serveur.get("message"))


if __name__ == "__main__":
    CLIENT_SOCKET = create_socket()
    main()













