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
    with open( file_path, "w" ) as file:
        file.write( message.as_string() )


def send_outside_mail(sender, recipient, message):
    data = {}
    try:
        util.send_mail( sender, recipient, message )
    except:
        data = {"status": False, "message": "Le courriel n'a pas pu être envoyé"}
    else:
        data = {"status": True, "message": f"Le courriel a été envoyé à {recipient} avec succès"}
    finally:
        send_message_to_client( str( data ) )


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
    recipient_host = recipient.split( '@' )[1]
    return recipient_host == "ift.glo2000.ca"


def send_mail(sender, recipient, subject, body):
    if not is_email_adress_valid( recipient ):
        data = {"status": False, "message": "L'adresse email du destinataire est invalide"}
        send_message_to_client( str( data ) )
        return

    message = util.get_message_MIME( sender, recipient, subject, body )

    if is_address_local( recipient ):
        send_local_mail( recipient, message )
    else:
        send_outside_mail( sender, recipient, message )


def get_mail_list_from_files(files):
    mails = dict()
    i = 1
    for file in files:
        mail = util.create_MIME_File( file )
        mails.update( {i: mail} )
        i += 1
    return mails


def get_user_mail_file_paths(username):
    path = f"{username}/"
    files = util.get_files_directory( path )
    files.remove( f"{path}config.txt" )
    return files


def get_user_mail_list(username):
    mail_paths = get_user_mail_file_paths( username )
    mails = get_mail_list_from_files( mail_paths )
    return mails


def get_user_directory_size(username):
    path = f"{username}/"
    return util.get_directory_size( path )


def get_subject_list_mail(mail_list):
    subjects = dict()
    for i in range( 1, len( mail_list ) + 1 ):
        mail = mail_list.get( i )
        subject = util.get_subject_of_mail( mail )
        subjects.update({i: subject})

    return subjects


def send_stats(username):
    nbr_mails = get_nbr_mails(username)
    mail_list = get_user_mail_list(username)
    subject_list = get_subject_list_mail(mail_list)
    size_directory = get_user_directory_size(username)
    data = {"status": True, "username": username, "nbr_mails": nbr_mails, "size_directory": size_directory,
            "mail_list": subject_list, "message": "Les statistiques ont bien été receuillies."}
    send_message_to_client(str(data))


def get_mail_content(mail):
    lines = mail.as_string().split('\n')
    sender = lines[3]
    subject = lines[5]
    recipient = lines[4]
    body = '\n'
    skipped_lines = {0, 1, 2, 3, 4, 5}
    for i, line in enumerate(lines):
        if i in skipped_lines:
            continue
        body += line
    mailContent = {"sender": sender, "recipient": recipient, "subject": subject, "body": body}
    return mailContent


def check_mails(username):
    mails = get_user_mail_list(username)
    if not mails:
        data = {"status": False, "message": "Votre boite de courriel est vide."}
        send_message_to_client(str(data))
        return

    mail_contents = dict()
    for i in mails:
        mail_contents.update({i: get_mail_content(mails.get(i))})

    data = {"status": True, "mail_list": mail_contents, "message": "Vous avez bien accédé aux courriels"}
    send_message_to_client(str(data))


def receive_message_from_client():
    try:
        return eval(CONNECTION.recv(1024).decode())
    except:
        return -1


def main():
    if not util.check_file_exists("ERREUR/"):
        util.create_directory("ERREUR")
    login_failed = False

    while True:
        data_account = receive_message_from_client()
        if data_account == -1:
            loginFailed = True
            break

        if data_account.get("command") == "login":
            if login(data_account.get("username"), data_account.get("password")):
                break

        elif data_account.get("command") == "signup":
            if create_account(data_account.get("username"), data_account.get("password")):
                break

    while True:
        if login_failed:
            break
        data_command = receive_message_from_client()
        if data_command == -1:
            break
        if data_command.get("command") == "send_mail":
            sender = data_command.get("sender")
            recipient = data_command.get("recipient")
            subject = data_command.get("subject")
            body = data_command.get("body")
            send_mail(sender, recipient, subject, body)
        elif data_command.get("command") == "check_mails":
            username = data_command.get("username")
            check_mails(username)
        elif data_command.get("command") == "check_stats":
            username = data_command.get("username")
            send_stats(username)
        elif data_command.get("command") == "quit":
            break


def start_socket(serverSocket):
    print("Démarrage du serveur...")
    serverSocket.listen(5)
    print(f"Écoute sur le port {PORT}")


if __name__ == "__main__":
    PORT = get_parser().port
    SERVER_SOCKET = create_new_socket()
    start_socket(SERVER_SOCKET)
    while True:
        CONNECTION, ADDRESS = SERVER_SOCKET.accept()
        main()
