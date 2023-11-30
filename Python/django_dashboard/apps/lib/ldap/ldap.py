"""
Low-level LDAP hooks.
"""
 
import ldap3
 
from contextlib import contextmanager
 
from django.contrib.auth import get_user_model
 
from django_python3_ldap.conf import settings
from django_python3_ldap.utils import import_func
 
from django.apps import apps as django_apps
from django_python3_ldap.ldap import Connection
from common_utils.django_util import Django_Util
class Connection(Connection):
 
    """
    A connection to an LDAP server.
    """
 
    def _get_or_create_user(self, user_data):
        """
        Returns a Django user for the given LDAP user data.
 
        If the user does not exist, then it will be created.
        
        Also will grant user for group permissions based on the ldap-group which this user belong to 
        """
        User = get_user_model()
        attributes = user_data["attributes"]
        print(settings.LDAP_AUTH_USER_FIELDS.items())
        # Create the user data.
        user_fields = {
            field_name: attributes.get(attribute_name, ("",))[0]
            for field_name, attribute_name
            in settings.LDAP_AUTH_USER_FIELDS.items()
        }
        user_fields = import_func(settings.LDAP_AUTH_CLEAN_USER_DATA)(user_fields)
        
        # Get Ldap group which this user belong to
        common_names = []
        for member in attributes.get("memberOf", ("",)):
            common_names.append(member.split(',')[0][member.index('CN=')+3:])                     
        LdapGroup =  django_apps.get_model('healthcheck.LdapGroup')
        user_ldap_group = LdapGroup.objects.filter(name__in = common_names)
        
        
        # Create the user lookup.
        user_lookup = {
            field_name: user_fields.pop(field_name, "")
            for field_name
            in settings.LDAP_AUTH_USER_LOOKUP_FIELDS
        }
        # Update or create the user.
        user, created = User.objects.update_or_create(
            defaults = user_fields,
            **user_lookup
        )
        # Update relations
        import_func(settings.LDAP_AUTH_SYNC_USER_RELATIONS)(user, attributes)
        user.is_staff = True
        # Clean up user group table
        auth_group_attached_ldap_ids = []
        for ldapgroup in LdapGroup.objects.all():
            for auth_group in ldapgroup.auth_groups.all():
                if not auth_group.id in auth_group_attached_ldap_ids:
                    auth_group_attached_ldap_ids.append(auth_group.id)
        for usergroup in user.groups.filter(id__in = auth_group_attached_ldap_ids):
            user.groups.remove(usergroup)
        # Add user group map
        for ladpgroup in user_ldap_group:
            auth_groups = ladpgroup.auth_groups.all()
            for auth_group in auth_groups:
                user.groups.add(auth_group)
        # All done!
        user.save()
        # Create user in ConfigModifier app
        self.createConfigModifierUser(user);
        # Add user to team users base on user ladp group
        self.addTeamUserByLdap(user, user_ldap_group)             
        return user
    def addTeamUserByLdap(self, user, ldap_groups):
        Team =  django_apps.get_model('healthcheck.Team')
        allTeams = Team.objects.all();
        for ldap_group in ldap_groups:
            for team in allTeams:
                if ldap_group not in team.ldap_groups.all():
                    continue
                if user not in team.users.all():
                    team.users.add(user)

    def createConfigModifierUser(self, user):
        
        GdUser =  Django_Util.getModel('ConfigModifier', 'GdUser')
        if GdUser and user:
            if user.username and not GdUser.objects.filter(login=user.username.strip()).first():
                GdUser.objects.create(login=user.username.strip(),empowered=False,cm = False)
 
@contextmanager
def connection(**kwargs):
    """
    Creates and returns a connection to the LDAP server.
 
    The user identifier, if given, should be keyword arguments matching the fields
    in settings.LDAP_AUTH_USER_LOOKUP_FIELDS, plus a `password` argument.
    """
    # Format the DN for the username.
    username = None
    password = None
    if kwargs:
        password = kwargs.pop("password")
        username = import_func(settings.LDAP_AUTH_FORMAT_USERNAME)(kwargs)
    # Make the connection.
    if username or password:
        if settings.LDAP_AUTH_USE_TLS:
            auto_bind = ldap3.AUTO_BIND_TLS_BEFORE_BIND
        else:
            auto_bind = ldap3.AUTO_BIND_NO_TLS
    else:
        auto_bind = ldap3.AUTO_BIND_NONE
    try:
        with ldap3.Connection(ldap3.Server(settings.LDAP_AUTH_URL), user=username, password=password, auto_bind=auto_bind) as c:
            yield Connection(c)
    except (ldap3.LDAPBindError, ldap3.LDAPSASLPrepError):
        yield None
 
 
def authenticate(**kwargs):
    """
    Authenticates with the LDAP server, and returns
    the corresponding Django user instance.
 
    The user identifier should be keyword arguments matching the fields
    in settings.LDAP_AUTH_USER_LOOKUP_FIELDS, plus a `password` argument.
    """
    password = kwargs.pop("password")
    # Check that this is valid login data.
    if not password or frozenset(kwargs.keys()) != frozenset(settings.LDAP_AUTH_USER_LOOKUP_FIELDS):
        return None
    # Connect to LDAP.
    with connection(password=password, **kwargs) as c:
        
        if c is None:
            return None
        return c.get_user(**kwargs)