import socket
import optparse
import sys
import util


def get_parser():
    parser = optparse.OptionParser()
    parser.add_option( "-p", "--port", dest="port", type=int, default=1400,
                       help="Port pour écouter et envoyer des messages" )
    return parser.parse_args( sys.argv[1:] )[0]


def create_user_config_file(username, password):
    util.create_directory( username )

    file_path = f"{username}/config.txt"
    with open( file_path, "w" ) as file:
        password_hashed = util.hash_password( password )
        file.write( password_hashed )


def does_password_match(password, file_path):
    with open( file_path, "r" ) as file:
        good_password_hash = file.readline()
        hash_entered = util.hash_password( password )
        return hash_entered == good_password_hash


def send_message_to_client(message):
    CONNECTION.send( message.encode() )


def login_attempt(username, password):
    if username == "":
        message = "Le nom d'utilisateur ne peut pas etre vide"
        return False, message

    file_path = f"{username}/config.txt"
    if not util.check_file_exists( file_path ):
        message = "Le nom d'utilisateur entré n'existe pas"
        return False, message

    if not does_password_match( password, file_path ):
        message = "Le mot de passe entré est invalide"
        return False, message

    message = f"Bonjour {username}"
    return True, message


def login(username, password):
    login_succesfull, message = login_attempt( username, password )
    data = {"status": login_succesfull, "message": message}
    send_message_to_client( str( data ) )

    return login_succesfull


def is_username_valid(username):
    path = f"{username}/config.txt"
    return not util.check_file_exists( path )


def is_email_adress_valid(address):
    regex = r"^[^@]+@[^@]+\.[^@]+$"
    return util.search_string( regex, address )


def does_account_exists(username):
    return util.check_file_exists( f"{username}/config.txt" )


def is_password_valid(password):
    regex = "^(?=.*[a-z])(?=.*[A-Z])(?=(.*?\d){2})[a-zA-Z\d]{6,14}$"
    return util.search_string( regex, password )


def create_new_socket():
    server_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    server_socket.bind( ("localhost", PORT) )
    return server_socket


def create_account(username, password):
    account_created = False
    if username == "":
        data = {"status": False, "message": "Le nom d'utilisateur de ne peut pas etre vide"}

    elif does_account_exists( username ):
        data = {"status": False, "message": "Ce compte existe déjà."}

    elif not is_password_valid( password ):
        data = {"status": False, "message": "Veuillez entrer un mot de passe conforme. Celui-ci doit contenir de 6 à "
                                            "14 caractères, au moins une lettre majuscule et 2 chiffres."}

    else:
        create_user_config_file( username, password )
        account_created = True
        data = {"status": True, "message": "Votre compte a été créé!"}

    send_message_to_client( str( data ) )
    return account_created


def check_login_command(login_command):
    return login_command == "1" or login_command == "2"


def get_nbr_mails(recipient):
    path = f"{recipient}/"
    return util.get_number_files_directory( path ) - 1


def create_mail_file(file_path, message):
    with open(file_path, "w") as file:
        file.write(message.as_string())


def send_outside_mail(sender, recipient, message):
    data = {}
    try:
        util.send_mail(sender, recipient, message )
    except:
        data = {"status": False, "message": "Le courriel n'a pas pu être envoyé"}
    else:
        data = {"status": True, "message": f"Le courriel a été envoyé à {recipient} avec succès"}
    finally:
        send_message_to_client(str(data))


def send_local_mail(recipient, message):
    if not util.check_file_exists( f"{recipient}/config.txt" ):
        directory_path = "ERREUR/"
        data = {"status": False,
                "message": "Le destinataire n'existe pas. Votre message a été mis dans le dossier 'ERREUR'"}
        send_message_to_client( str( data ) )
        nbr_mails = util.get_number_files_directory( directory_path )

    else:
        directory_path = f"{recipient}/"
        data = {"status": True, "message": "Le courriel a été envoyé"}
        send_message_to_client( str( data ) )
        nbr_mails = get_nbr_mails( recipient )

    file_path = f"{directory_path}/{nbr_mails + 1}"
    create_mail_file( file_path, message )


def is_address_local(recipient):
    recipient_host = recipient.split('@')[1]
    return recipient_host == "ift.glo2000.ca"


def send_mail(sender, recipient, subject, body):
    if not is_email_adress_valid(recipient):
        data = {"status": False, "message": "L'adresse email du destinataire est invalide"}
        send_message_to_client(str(data))
        return

    message = util.get_message_MIME(sender, recipient, subject, body)

    if is_address_local(recipient):
        send_local_mail(recipient, message)
    else:
        send_outside_mail(sender, recipient, message)


def get_user_directory_size(username):
    path = f"{username}/"
    return util.get_directory_size(path)





