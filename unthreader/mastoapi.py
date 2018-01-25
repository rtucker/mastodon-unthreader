#!/usr/bin/env python3

import getpass
import mastodon
import pathlib

APP_NAME = "unthreader"

APP_SCOPES = ['read']

INSTANCE_FILE = "unthreader_instance.config"
CLIENTCRED_FILE = "unthreader_clientcred.secret"
USERCRED_FILE = "unthreader_usercred.secret"

def is_configured(config_path):
    p = pathlib.Path(config_path)

    return (p.exists() and
            p.joinpath(INSTANCE_FILE).exists() and
            p.joinpath(CLIENTCRED_FILE).exists() and
            p.joinpath(USERCRED_FILE).exists())

def get_instance(config_path):
    p = pathlib.Path(config_path)

    if p.joinpath(INSTANCE_FILE).exists():
        with open(p.joinpath(INSTANCE_FILE), 'r') as fp:
            return fp.readline().strip()

    return None

def ask_correct():
    confirm = input('Is this correct? [Y/n] ')

    return confirm in ['Y', 'y', '']

def generate_config(config_path):
    p = pathlib.Path(config_path)

    if not p.is_dir():
        raise RuntimeError("config_path is not a valid directory: '%s'" % p)

    instance = get_instance(p)
    force_new = False

    if instance is not None:
        print("Your instance is: %s" % instance)

        if not ask_correct():
            instance = None

    while not instance:
        inst_raw = ''
        while len(inst_raw) == 0:
            print("Please enter the hostname of your Mastodon instance.")
            inst_raw = input('--> https://')

        instance = 'https://' + inst_raw

        print("You entered: %s" % instance)

        if ask_correct():
            instance = None
        else:
            with open(p.joinpath(INSTANCE_FILE), 'w') as fp:
                fp.write(instance)
                fp.write('\n')
            force_new = True

    print("Selected instance: %s" % instance)

    # create client/app credentials
    if force_new or not p.joinpath(CLIENTCRED_FILE).exists():
        print("Registering application with instance...")
        mastodon.Mastodon.create_app(APP_NAME,
            scopes=APP_SCOPES,
            api_base_url=instance,
            to_file=p.joinpath(CLIENTCRED_FILE))

    # Log in
    if force_new or not p.joinpath(USERCRED_FILE).exists():
        md = mastodon.Mastodon(
            client_id=p.joinpath(CLIENTCRED_FILE),
            api_base_url=instance)

        print("Logging into %s..." % instance)

        method = input('Use web-based method to log in? (For 2FA users) [Y/n] ')
        if method in ['N', 'n']:
            username = input('E-mail address: ')
            password = getpass.getpass('Password: ')
            print("Logging in...")
            md.log_in(username, password,
                to_file=p.joinpath(USERCRED_FILE),
                scopes=APP_SCOPES)

        else:
            url = md.auth_request_url(
                client_id=p.joinpath(CLIENTCRED_FILE),
                scopes=APP_SCOPES)

            print("URL: %s" % url)

            auth_code = input("Enter the authorization code: ")
            md.log_in(code=auth_code,
                to_file=p.joinpath(USERCRED_FILE),
                scopes=APP_SCOPES)

def get_mastodon(config_path):
    """Returns a Mastodon connection object."""
    p = pathlib.Path(config_path)

    instance = get_instance(p)

    if instance is None or not is_configured(config_path):
        raise RuntimeError("You must call generate_config first")

    return mastodon.Mastodon(
            client_id=p.joinpath(CLIENTCRED_FILE),
            api_base_url=instance,
            access_token=p.joinpath(USERCRED_FILE))
