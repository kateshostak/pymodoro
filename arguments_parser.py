import argparse


class RunParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--name', required=True)
        self.parser.add_argument('--setting', required=True)

    def parse_args(self, args):
        return self.parser.parse_args(args)


class NewParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--name', required=True)
        self.parser.add_argument('--settings', required=True)
        self.parser.add_argument('--work', type=int, required=True)
        self.parser.add_argument('--shortbreak', type=int, required=True)
        self.parser.add_argument('--longbreak', type=int, required=True)
        self.parser.add_argument('--cycle', type=int, required=True)

    def parse_args(self, args):
        return self.parser.parse_args(args)


class UpdateParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--name', required=True)
        self.parser.add_argument('--settings', required=True)
        self.parser.add_argument('--work', type=int, default=None)
        self.parser.add_argument('--shortbreak', type=int, default=None)
        self.parser.add_argument('--longbreak', type=int, default=None)
        self.parser.add_argument('--cycle', type=int, default=None)

    def parse_args(self, args):
        return self.parser.parse_args(args)


class DeleteParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--name', required=True)

    def parse_args(self, args):
        return self.parser.parse_args(args)


class ArgParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser(prefix_chars='+')
        self.parser.add_argument('command')
        self.parser.add_argument('args', nargs='*')

    def parse_args(self, *args):
        if args:
            args = self.parser.parse_args(args[0])
        else:
            args = self.parser.parse_args()
        return args.command, self.subparse_args(args.command, args.args)

    def subparse_args(self, command, args):
        subparser_wrapper = SubparserManager(command)
        if not subparser_wrapper.subparser:
            self.parser.print_help()
        else:
            return subparser_wrapper.parse_args(args)


class SubparserManager():
    RUN = 'run'
    NEW = 'new'
    UPDATE = 'update'
    DELETE = 'delete'
    command_to_subparser = {
            RUN: RunParser,
            NEW: NewParser,
            UPDATE: UpdateParser,
            DELETE: DeleteParser
            }

    def __init__(self, command):
        self.subparser = self.get_subparser(command)

    def get_subparser(self, command):
        if command in SubparserManager.command_to_subparser:
            subparser = SubparserManager.command_to_subparser[command]()
            return subparser
        else:
            return None

    def parse_args(self, args):
        return self.subparser.parse_args(args)


def main():
    argparser = ArgParser()
    command, args = argparser.parse_args()
    print(command, args)


if __name__ == '__main__':
    main()
