import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--test', dest='test', nargs='?', default=False, const=True, help='If the program should save on calendar or just get matches from FIP website')