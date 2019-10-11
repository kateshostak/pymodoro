import argparse
from arguments_parser import ArgParser


def argument_parser_test(command, args, check_args):
    pargs = [command, *args.split()]
    parser = ArgParser()
    ca = argparse.Namespace()
    for key, value in check_args.items():
        ca.__setattr__(key, value)
    parsed_command, parsed_args = parser.parse_args(pargs)
    print(parsed_args)
    if command == parsed_command and parsed_args == ca:
        return True

def main():
    check_args = {'name':'kate', 'setting':'work'}
    command = 'run'
    subargs = '--name kate --setting work'
    if not argument_parser_test(command, subargs, check_args):
        print(f'Argument parsing failed with command:{command} and args:{args}')

if __name__ == '__main__':
    main()
