#!/usr/bin/env python
import sys;
import bcrypt;
import argparse;

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser(description='Encodes a password with BCrypt')

parser.add_argument('-p', '--password', dest='password', metavar='password', required=True, help='The password to encode')
parser.add_argument('-s', '--salt', dest='salt', metavar='salt', required=False, help='The salt to use in BCrypt. Generated automatically if not provided')
parser.add_argument('-r', '--rounds', dest='rounds', type=int, metavar='rounds', required=False, help='The number of rounds to use when generating salt')
parser.add_argument('--show', dest='show', action='store_true', required=False, help='Displays generated salt')

args = parser.parse_args()

password=args.password
salt=args.salt
rounds=args.rounds
show=args.show

if (salt != None) and (rounds != None):
    print(bcolors.WARNING + "WARN: Ignoring rounds since salt specified")

if (salt == None):
    if (rounds == None):
        rounds=10
    salt = bytes(bcrypt.gensalt(rounds))
    if show:
        print("Generated salt after %d rounds: %s" % (rounds,salt.decode()))
else:
    salt = salt.encode('utf-8')
    if show:
        print("User salt: %s" % salt.decode())

password = bcrypt.hashpw(password.encode('utf-8'), salt)
print(password.decode())
