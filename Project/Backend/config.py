from configparser import ConfigParser
import os

def config(filename, section='postgresql'):
    if os.path.isfile(filename):
        parser = ConfigParser()
        parser.read(filename)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return f'postgresql+psycopg2://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'