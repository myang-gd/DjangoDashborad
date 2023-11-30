from django.db import models

# Create your models here.


class QueryScript(models.Model):
    name = models.CharField(max_length=128, unique=True, db_column='Name')
    created_date = models.DateTimeField(db_column='Created_Date', auto_now_add=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    sql = models.TextField(db_column='Sql', blank=True, null=True)
    category = models.CharField(max_length=128, db_column='Category', blank=True, null=True)
    created_by = models.CharField(max_length=128, db_column='Created_by', blank=True, null=True)
    share = models.BooleanField(db_column='Share', default=True)
    locked = models.BooleanField(db_column='Locked', default=False)
    databases = models.TextField(db_column='Databases', blank=True, null=True)
    target = models.CharField(max_length=128, db_column='Target', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'QueryScript'


class TargetDatabasesMapping(models.Model):
    target = models.CharField(max_length=128, db_column='Target', blank=False, null=False)
    databases = models.TextField(db_column='Databases', blank=True, null=True)

    def __str__(self):
        return self.target

    class Meta:
        db_table = 'TargetDatabasesMapping'


class Database(models.Model):
    DB_TYPE = [
        ('MSSQL', 'Microsoft SQL Server'),
        ('MYSQL', 'Mysql'),
        ('MONGOD', 'MongoDb'),
        ('POSTGRE', 'Postgresql'),
        ('CASSANDRA', 'Cassandra'),
    ]
    name = models.CharField(max_length=50, unique=True, db_column='Name')
    created_date = models.DateTimeField(db_column='Created_Date', auto_now_add=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    server = models.CharField(max_length=128, db_column='Server', blank=True, null=True)
    database = models.CharField(max_length=128, db_column='Database', blank=True, null=True)
    username = models.CharField(max_length=128, db_column='Username', blank=True, null=True)
    password = models.CharField(max_length=128, db_column='Password', blank=True, null=True)
    conn_properties = models.CharField(max_length=128, db_column='Conn_properties', blank=True, null=True)
    created_by = models.CharField(max_length=128, db_column='Created_by', blank=True, null=True)
    disabled = models.BooleanField(db_column='Disabled', default=False)

    type = models.CharField(
        max_length=10,
        choices=DB_TYPE,
        default='SQL',
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Database'


class UserProfile(models.Model):
    user = models.CharField(max_length=128, db_column='User', null=False, blank=False, unique=True)
    profile = models.CharField(max_length=128, db_column='profile', null=False, blank=False, unique=True)

    class Meta:
        db_table = 'UserProfile'

    def __str__(self):
        return self.user + ' :: profile'


class Favorite(models.Model):
    profile = models.ForeignKey(UserProfile, null=False, blank=False, on_delete=models.CASCADE)
    favorites = models.ForeignKey(QueryScript, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Favorite'
        unique_together = ('profile', 'favorites',)

    def __str__(self):
        return self.profile.user + ' :: favorites -> ' + self.favorites.name


class Recent(models.Model):
    profile = models.ForeignKey(UserProfile, null=False, blank=False, on_delete=models.CASCADE)
    created_date = models.DateTimeField(db_column='Created_Date', auto_now_add=True)
    query_script = models.ForeignKey(QueryScript, on_delete=models.CASCADE)
    parameters = models.CharField(max_length=1024, db_column='parameters', blank=True, null=True)

    class Meta:
        db_table = 'Recent'

    def __str__(self):
        return self.profile.user + ' :: recent ->' + self.query_script.name


#views
class CategoryName(models.Model):
    category = models.CharField(max_length=128, db_column='Category', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'View_Category'


class DatabaseName(models.Model):
    dbName = models.CharField(max_length=128, db_column='DbName', blank=True, null=True)
    relName = models.CharField(max_length=128, db_column='RelName', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'View_DatabaseName'


class EnvDbMapping(models.Model):
    env = models.CharField(max_length=128, db_column='Env', blank=True, null=True)
    dbName = models.CharField(max_length=128, db_column='DbName', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'View_EnvDbMapping'


class ExecuteHistory(models.Model):
    name = models.CharField(max_length=128, unique=True, db_column='Name')
    sql = models.TextField(db_column='Sql', blank=True, null=True)
    target_server = models.CharField(max_length=256, db_column='Target_Server')
    executor = models.CharField(max_length=128, db_column='Executor', blank=True, null=True)
    executed_date = models.DateTimeField(db_column='Executed_Date', auto_now_add=True)
    ip_address = models.CharField(max_length=128, db_column='IP_Address')

    class Meta:
        db_table = 'ExecuteHistory'

    def __str__(self):
        return self.executor + ' :: ' + self.name

