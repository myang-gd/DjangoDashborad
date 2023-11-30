class DBRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read cucumber models go to cukes_runner.
        """
        if model._meta.app_label == 'healthcheck':
            return 'default'
        elif model._meta.app_label == 'qa_monitor':
            return 'qa_monitor'
        elif model._meta.app_label == 'ConfigModifier':
            return 'config_lock'
        elif model._meta.app_label == 'query_view' or \
                model._meta.app_label == 'query_api':
            return 'GDCAUTO'
        elif model._meta.app_label == 'MilestoneAPI':
            return 'automation'
        else:
            return None
        
    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'healthcheck':
            return 'default'
        elif model._meta.app_label == 'qa_monitor':
            return 'qa_monitor'
        elif model._meta.app_label == 'ConfigModifier':
            return 'config_lock'
        elif model._meta.app_label == 'query_view' or \
                model._meta.app_label == 'query_api':
            return 'GDCAUTO'
        elif model._meta.app_label == 'MilestoneAPI':
            return 'automation'
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'healthcheck' or \
           obj2._meta.app_label == 'healthcheck':
            return True
       
        elif obj1._meta.app_label == 'qa_monitor' or \
            obj2._meta.app_label == 'qa_monitor':
            return True
        elif obj1._meta.app_label == 'ConfigModifier' or \
            obj2._meta.app_label == 'ConfigModifier':
            return True
        elif obj1._meta.app_label == 'query_view' or \
                obj2._meta.app_label == 'query_api':
            return True
        else:
            return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """        
        if app_label == 'healthcheck':
            return db == 'default'
        
        elif app_label == 'qa_monitor':
            return db == 'qa_monitor'
        elif app_label == 'ConfigModifier':
            return db == 'config_lock'
        elif app_label == 'query_view':
            return db == 'GDCAUTO'
        else:
            return None