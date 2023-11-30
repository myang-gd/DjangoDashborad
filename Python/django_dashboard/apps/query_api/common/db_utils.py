# Create db mapping
from apps.query_view.models import EnvDbMapping


class DbUtils:
    def __init__(self):
        self.env_2_db = {}
        self.db_2_env = {}
        env_db_mapping = EnvDbMapping.objects.all()
        for map in env_db_mapping:
            if map['env'] not in self.env_2_db:
                self.env_2_db[map['env']] = []
            self.env_2_db[map['env']].append(map['dbName'])

            if map['dbName'] not in self.db_2_env:
                self.db_2_env[map['dbName']] = []
            self.db_2_env[map['dbName']].append(map['env'])

    def get_envs(self, database):
        return self.db_2_env[database]

    def get_database(self, env):
        return self.env_2_db[env]



