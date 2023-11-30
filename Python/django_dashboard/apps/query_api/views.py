import base64
import json
import re
from datetime import datetime

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers, viewsets, permissions
# Serializers define the API representation.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.query_view.models import QueryScript, Database, UserProfile, Favorite, ExecuteHistory
from common_utils.database_agents import DatabaseAgents


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff', 'is_superuser']


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Serializers define the API representation.
class QueryScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryScript
        fields = ['id', 'name', 'description', 'sql', 'category', 'target', 'share', 'locked', 'databases',
                  'created_by']


# ViewSets define the view behavior.
class QueryScriptViewSet(viewsets.ModelViewSet):
    queryset = QueryScript.objects.all()
    serializer_class = QueryScriptSerializer


# Serializers define the API representation.
class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ['id', 'name', 'description', 'server', 'database', 'username', 'password', 'conn_properties',
                  'created_by', 'type']


# ViewSets define the view behavior.
class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer
    pagination_class = None
    permission_classes = [IsAdminUser]


# Serializers define the API representation.
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'profile']


# ViewSets define the view behavior.
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


# Serializers define the API representation.
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['profile', 'favorites']


# ViewSets define the view behavior.
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def my_queries(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        login_user = request.GET.get('login_user', r'')
        if login_user:
            user_id = initialize_user_profile_ifn(login_user)
        else:
            user_id = initialize_user_profile_ifn(request.user)
            login_user = str(request.user)
        user_id = initialize_user_profile_ifn(request.user)
        sql = "SELECT A.id id,A.Name name,A.Created_Date created_date," \
              "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
              "A.Share share,A.Locked locked,A.Databases databases,A.[Target] target,isnull(F.id,0) is_favorite " \
              " FROM [QueryStore].[dbo].[QueryScript] A " \
              "left join [QueryStore].[dbo].[Favorite] F ON F.favorites_id = A.id and F.profile_id ={0}" \
              "where A.Created_by = '{1}' ".format(str(user_id), login_user)
        dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
        script = fmt_query_result(dal.execute(sql), login_user)
        return Response(script)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def favorite_queries(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        login_user = request.GET.get('login_user', r'')
        if login_user:
            user_id = initialize_user_profile_ifn(login_user)
        else:
            user_id = initialize_user_profile_ifn(request.user)
            login_user = str(request.user)
        sql = "SELECT A.id id,A.Name name,A.Created_Date created_date," \
              "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
              "A.Share share,A.Locked locked,A.Databases databases,A.[Target] target, isnull(B.id,0) is_favorite " \
              "FROM [QueryStore].[dbo].[QueryScript] A " \
              "join [QueryStore].[dbo].[Favorite] B ON B.favorites_id = A.id " \
              "join [QueryStore].[dbo].[UserProfile] C ON B.profile_id = C.id " \
              "where C.[User]='{0}' ".format(login_user)

        dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
        script = fmt_query_result(dal.execute(sql), login_user)
        return Response(script)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def recent_queries(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        login_user = request.GET.get('login_user', r'')
        if login_user:
            user_id = initialize_user_profile_ifn(login_user)
        else:
            user_id = initialize_user_profile_ifn(request.user)
            login_user = str(request.user)

        sql = "SELECT A.id id,A.Name name,A.Created_Date created_date," \
              "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
              "A.Share share,A.Locked locked,A.Databases databases,A.[Target] target,isnull(F.id,0) is_favorite " \
              " FROM [QueryStore].[dbo].[QueryScript] A " \
              "left join [QueryStore].[dbo].Recent B ON A.id = B.query_script_id " \
              "left join [QueryStore].[dbo].[UserProfile] C ON B.profile_id = C.id " \
              "left join [QueryStore].[dbo].[Favorite] F ON F.favorites_id = A.id " \
              "where User='{0}' order by B.Created_Date ".format(login_user)

        dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
        script = fmt_query_result(dal.execute(sql), login_user)
        return Response(script)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def search_queries(request):
    """
    List all code snippets, or create a new snippet.
    """
    enable_mem = request.GET.get('enable_mem', r'false')
    condition = request.GET.get('condition', r'')
    login_user = request.GET.get('login_user', r'')
    if login_user:
        user_id = initialize_user_profile_ifn(login_user)
    else:
        user_id = initialize_user_profile_ifn(request.user)
        login_user = str(request.user)

    if request.method == 'GET':
        if enable_mem == 'true':
            memcached_query()
            data_query = fmt_query_result(cache.get('query_mem'), login_user)
            data_favorite = cache.get('favorite_mem')
            for item in data_query:
                if request.user in data_favorite and item['id'] in data_favorite[request.user]:
                    item['is_favorite'] = 1
                else:
                    item['is_favorite'] = 0
            filter_obj = data_query
            if condition and condition.strip():
                p = re.compile(condition, re.IGNORECASE)
                filter_obj = filter(lambda x: (p.match(str(x['name'])) or p.match(str(x['description']))
                                               or p.match(str(x['sql'])) or p.match(str(x['category']))
                                               or p.match(str(x['created_by'])) or p.match(str(x['target']))),
                                    data_query)
            return Response(filter_obj)
        else:
            sql = "SELECT A.id id,A.Name name,A.Created_Date created_date," \
                  "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
                  "A.Share share,A.Locked locked,A.Databases databases,A.[Target] target,isnull(F.id,0) is_favorite " \
                  "FROM [QueryStore].[dbo].[QueryScript] A " \
                  "left join [QueryStore].[dbo].[Favorite] F ON F.favorites_id = A.id and F.profile_id =" + str(user_id)

            if condition != '':
                sql += "where A.Share=1 and (A.Name like '%{0}%' OR A.Description like '%{0}%' " \
                       "OR A.sql like '%{0}%' OR A.Category like '%{0}%' " \
                       "OR A.Created_by like '%{0}%' OR A.[Target] like '%{0}%')".format(condition)
            sql += " order by A.id"

            dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
            script = fmt_query_result(dal.execute(sql), login_user)
        return Response(script)


def memcached_query():
    data_query = cache.get('query_mem')
    if not data_query:
        print("Flush memcached for query script")
        sql = "SELECT A.id id,A.Name name,A.Created_Date created_date," \
              "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
              "A.Share share,A.Locked locked,A.[Databases] databases," \
              "A.[Target] target FROM [QueryStore].[dbo].[QueryScript] A " \
              "WHERE A.Share=1 "

        dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
        script = dal.execute(sql)
        cache.set('query_mem', script, 60 * 15)

    data_favorite = cache.get('favorite_mem')
    if not data_favorite:
        print("Flush memcached for favorite query script")
        sql = "SELECT isnull(G.[User],'') favorite_user,  A.id id,A.Name name,A.Created_Date created_date," \
              "A.Description description,A.sql,A.Category category,A.Created_by created_by," \
              "A.Share share,A.Locked locked,A.[Databases] databases,A.[Target] target " \
              "FROM [QueryStore].[dbo].[QueryScript] A " \
              "join [QueryStore].[dbo].[Favorite] F ON F.favorites_id = A.id " \
              "join [QueryStore].[dbo].[UserProfile] G ON F.profile_id = G.id " \
              "WHERE A.Share=1"

        dal = DatabaseAgents.database(Database.objects.get(name='QueryStore').id)
        favorites = dal.execute(sql)
        favorites_user = {}
        for item in favorites:
            if item['favorite_user'] not in favorites_user:
                favorites_user[item['favorite_user']] = []
            favorites_user[item['favorite_user']].append(item['id'])
        cache.set('favorite_mem', favorites_user, 60 * 15)


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def sync_favorite(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        query_script_id = request.GET.get('query_script_id', r'')
        login_user = request.GET.get('login_user', r'')
    if request.method == 'POST':
        query_script_id = request.POST.get('query_script_id', r'')
        login_user = request.POST.get('login_user', r'')

    if login_user:
        user = UserProfile.objects.get(user=login_user)
    else:
        user = UserProfile.objects.get(user=request.user)

    fav = QueryScript.objects.filter(id=query_script_id)
    if not fav.exists():
        return Response({'failed': 'Input data is invalid.'})

    if request.method == 'GET':
        return Response({'is_favorite': Favorite.objects.filter(profile=user, favorites=fav[0]).exists()})

    if request.method == 'POST':
        is_favorite = request.POST.get('is_favorite', r'')
        fav_exist = Favorite.objects.filter(profile=user, favorites=fav[0]).exists()
        if is_favorite == 'true' and not fav_exist:
            print("Add favorite : %s " % fav[0].name)
            new_fav = Favorite(profile=user, favorites=fav[0])
            new_fav.save()
            return Response({'is_favorite': True, 'info':  "Add favorite : %s " % fav[0].name})
        elif is_favorite == 'false' and fav_exist:
            print("Remove favorite : %s " % fav[0].name)
            Favorite.objects.get(profile=user, favorites=fav[0]).delete()
            return Response({'is_favorite': False, 'info': "Remove favorite : %s " % fav[0].name})
        else:
            print('No action required')
            return Response({'info': 'No Action required', 'login_user': login_user})


def fmt_query_result(data, user):
    for row in data:
        try:
            if str(row['created_by']) == str(user):
                row['is_owner'] = True
            else:
                row['is_owner'] = False
            row['databases'] = json.loads(row['databases'])
        except Exception as e:
            print("%s %s %s %s" % (row['id'], row['name'], row['databases'], e))
            row['databases'] = []
            row['is_owner'] = 'false'
    return data


def initialize_user_profile_ifn(user):
    cur_user = UserProfile.objects.filter(user=user)
    if not cur_user.exists():
        new_user = UserProfile(user=user, profile='{"fav": 1, "recent": 0, "history": 1}')
        new_user.save()
        find_id = new_user.id
    else:
        find_id = cur_user[0].id
    return find_id


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def execute_query_from_case(request):
    result = {'data': [], 'success': True}
    if request.method == 'POST':
        print(request.POST.get('qry_name'), request.POST.get('qry_param'),
              request.POST.get('qry_db_name'), request.POST.get('env'))
        qry_name = request.POST.get('qry_name')
        qry_param = json.loads(request.POST.get('qry_param'))
        obj_query = QueryScript.objects.get(name=qry_name)
        sql = get_object_value(obj_query, 'sql')
        locked = get_object_value(obj_query, 'locked')
        target = get_object_value(obj_query, 'target')
        if 'qry_db_name' in request.POST and request.POST.get('qry_db_name').strip():
            qry_db_name = (request.POST.get('env') + "-" + request.POST.get('qry_db_name')).upper()
            qry_db_name_sw = (request.POST.get('env') + "_" + request.POST.get('qry_db_name')).upper()
            db_find = Database.objects.filter(Q(name=qry_db_name) | Q(name=qry_db_name_sw))
            if db_find.exists():
                db_find_id = db_find[0].id
                if len(db_find) > 1:
                    print('Multiple database get and will just use the first one : ' + db_find[0].name)
            else:
                raise Exception('Can not find database : ' + qry_db_name + ' or ' + qry_db_name_sw)
        else:
            qry_db_name = (request.POST.get('env') + "-" + target).upper()
            db_find_id = Database.objects.get(name=qry_db_name).id

        if not locked:
            obj_query.locked = True
            obj_query.save()
        if sql:
            try:
                db = DatabaseAgents.database(db_find_id)
                for key in qry_param:
                    sql = sql.replace('%{' + key + '}', qry_param[key])
                result['data'] = db.execute(sql, 100)
                if len(result['data']) == 0:
                    result['error'] = 'No data found in database!'

                ExecuteHistory.objects.create(name=get_object_value(obj_query, 'name'),
                                              sql=sql, executor='AutomationCase',
                                              ip_address=request.META.get("REMOTE_ADDR"),
                                              target_server=("%s/%s" % (db.db_server, db.db_database)))
            except Exception as e:
                result['data'] = []
                result['success'] = False
                result['error'] = str(e)

    return Response(result)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def sync_query_from_jvm(request):
    result = {'success': True, 'error': ''}
    if request.method == 'POST':
        dbs_list = get_databases_by_name_endswith(request.POST.get('database_group'))
        database_map = str(dbs_list).replace('\'', '"')

        obj_find = QueryScript.objects.filter(name=request.POST.get('qry_name'))
        if not obj_find.exists():
            try:
                QueryScript.objects.create(name=request.POST.get('qry_name'),
                                           description=request.POST.get('description'),
                                           category=request.POST.get('category'), sql=request.POST.get('sql'),
                                           target=request.POST.get('database_group'), share=True, locked=False,
                                           created_by=request.POST.get('created_by', 'JVM'),
                                           created_date=datetime.now(),
                                           databases=database_map)
            except Exception as e:
                result['success'] = False
                result['error'] = str(e)
        else:
            if obj_find[0].sql != request.POST.get('sql'):
                try:
                    find_query=QueryScript.objects.filter(name=request.POST.get('qry_name'))
                    find_query.update(sql=request.POST.get('sql'), created_by=request.POST.get('created_by', 'JVM'))
                except Exception as e:
                    result['success'] = False
                    result['error'] = str(e)
            else:
                print('Sql is no change and no action required.')
    return Response(result)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def execute_query(request):
    result = {'data': [], 'success': True, 'error': '', 'db_info': ''}
    if request.method == 'POST':
        data = json.loads(request.POST.get('my_json_data'))
        if 'login_user' in data:
            login_user = data['login_user']
            login_user_is_staff = User.objects.get(username=login_user).is_superuser
        else:
            login_user = request.user
            login_user_is_staff = request.user.is_superuser

        qry_script = QueryScript.objects.get(id=data['query_id'])
        sql = get_object_value(qry_script, 'sql')

        if sql != '':
            try:
                db = DatabaseAgents.database(data['db_id'])
                result['db_info'] = "%s/%s" % (db.db_server, db.db_database)
                for key in data['params']:
                    sql = sql.replace('%{' + key + '}', data['params'][key])
                result['data'] = db.execute(sql, limit=100)
                if len(result['data']) == 0:
                    result['error'] = 'No data found in database!'

                ExecuteHistory.objects.create(name=get_object_value(qry_script, 'name'),
                                              sql=sql, executor=login_user,
                                              ip_address=request.META.get("REMOTE_ADDR"),
                                              target_server=("%s/%s" % (db.db_server, db.db_database)))
            except Exception as e:
                result['data'] = []
                result['success'] = False
                result['error'] = str(e)
    return Response(result)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def cancel_query(request):
    result = {'data': '', 'success': True, 'error': ''}
    if request.method == 'POST':
        data = json.loads(request.POST.get('my_json_data'))
        qry_script = None
        if 'query_id' in data:
            qry_script = QueryScript.objects.get(id=data['query_id'])

        if qry_script is not None:
            query_name = get_object_value(qry_script, 'name')
        else:
            query_name = 'Unknown Name (debug)'
        session_name = str(base64.b64encode((str(request.user) + '_' + query_name + '_'
                                                         + str(request.META.get("REMOTE_ADDR"))
                                                         + '_validate').encode('ascii')))
        if session_name in request.session:
            del request.session[session_name]
            result['data'] = 'Deleted session :' + session_name
    return Response(result)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def debug_query(request):
    result = {'data': [], 'success': True, 'error': ''}
    if request.method == 'POST':
        data = json.loads(request.POST.get('my_json_data'))

        if 'login_user' in data:
            login_user = data['login_user']
            login_user_is_staff = User.objects.get(username=login_user).is_superuser
        else:
            login_user = request.user
            login_user_is_staff = request.user.is_superuser

        qry_script = None
        if 'query_id' in data:
            qry_script = QueryScript.objects.get(id=data['query_id'])

        if qry_script is not None:
            query_name = get_object_value(qry_script, 'name')
            sql = get_object_value(qry_script, 'sql')
            owner = get_object_value(qry_script, 'created_by')
        else:
            query_name = 'Unknown Name (debug)'
            owner = 'Unknown user'

        if 'query_script' in data:
            sql = data['query_script']

        if 'affect_allow_max_row' in data:
            affect_allow_max_row = int(data['affect_allow_max_row'])
        else:
            affect_allow_max_row = 10

        if sql != '':
            try:
                db = DatabaseAgents.database(data['db_id'])
                result['db_info'] = "%s/%s" % (db.db_server, db.db_database)
                for key in data['params']:
                    sql = sql.replace('%{' + key + '}', str(data['params'][key]))

                DatabaseAgents.validate(sql)

                if DatabaseAgents.is_insert(sql):
                    if owner != str(login_user) and not login_user_is_staff:
                        raise Exception('Just query owner and admin can do insert query')
                    print('Deal with insert')
                    db.execute_commit(sql)
                    result['data'] = [{'Insert': 'Insert record success!'}]
                    ExecuteHistory.objects.create(name=query_name,
                                                  sql=sql, executor=request.user,
                                                  ip_address=request.META.get("REMOTE_ADDR"),
                                                  target_server=("%s/%s" % (db.db_server, db.db_database)))

                elif DatabaseAgents.is_update(sql) or DatabaseAgents.is_delete(sql):
                    if owner != str(login_user) and not login_user_is_staff:
                        raise Exception('Just query owner and admin can do update/delete query')
                    print('Deal with update /delete')
                    curr_status = DatabaseAgents.validate_update_delete_query(data['db_id'], sql)

                    session_name = str(base64.b64encode((str(request.user) + '_' + query_name + '_'
                                                         + str(request.META.get("REMOTE_ADDR"))
                                                         + '_validate').encode('ascii')))

                    curr_status['affect_allow_max_row'] = affect_allow_max_row

                    if 'is_allow' not in data or not data['is_allow']:
                        result['session'] = session_name
                        result[session_name] = curr_status
                    else:
                        print('Commit query/delete ...', query_name)
                        cur_session = curr_status
                        if 'is_allow' in data:
                            cur_session['is_allow'] = data['is_allow']

                        if int(cur_session['affect_row']) <= affect_allow_max_row and cur_session['with_where']:
                            if cur_session['is_allow']:
                                db.execute_commit(sql)
                                result['data'] = [{'Update/Delete': 'Update/Delete record success! (Affected '
                                                                    + str(cur_session['affect_row']) + ' Records.)'}]
                                ExecuteHistory.objects.create(name=query_name,
                                                              sql=sql, executor=login_user,
                                                              ip_address=request.META.get("REMOTE_ADDR"),
                                                              target_server=("%s/%s" % (db.db_server, db.db_database)))
                        else:
                            if not cur_session['with_where']:
                                error_message = 'Not allow this action, because it has no where clause.\n'
                            else:
                                error_message = 'Not allow this action, because it will impact more than ' \
                                                + str(affect_allow_max_row) + ' records.\n There are ' \
                                                + str(cur_session['affect_row']) + ' records will be affected.'
                            raise Exception(error_message)

                else:
                    result['data'] = db.execute(sql, limit=100)
                    ExecuteHistory.objects.create(name=query_name,
                                                  sql=sql, executor=login_user,
                                                  ip_address=request.META.get("REMOTE_ADDR"),
                                                  target_server=("%s/%s" % (db.db_server, db.db_database)))
            except Exception as e:
                result['data'] = []
                result['success'] = False
                result['error'] = str(e)
    return Response(result)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def save_query(request):
    return_date = {"success": True}
    try:
        if request.method == 'POST':
            data = json.loads(request.POST.get('my_json_data'))
            selected_db = data['database']
            if 'login_user' in data:
                login_user = data['login_user']
                login_user_is_staff = User.objects.get(username=login_user).is_superuser
            else:
                login_user = request.user
                login_user_is_staff = request.user.is_superuser

            dbs_list = get_databases_by_name_endswith(selected_db)
            dbs_list_str = str(dbs_list).replace('\'', '"')
            # update query
            if 'update' in data and str(data['update']).lower() == "true":
                find_query = QueryScript.objects.filter(id=data['id'])
                if find_query.exists():
                    if str(find_query[0].created_by) == str(login_user) or login_user_is_staff:
                        find_query.update(name=data['name'],
                                          description=data['description'],
                                          category=data['category'],
                                          sql=data['sql'],
                                          share=data['share'],
                                          target=selected_db,
                                          databases=dbs_list_str
                                          )
                    else:
                        raise Exception("You can't update query that own by others.")
                else:
                    raise Exception("Can't find query by given id: %s. This query maybe does not exists." % data['id'])
            else:
                QueryScript.objects.create(name=data['name'], description=data['description'],
                                           category=data['category'],
                                           sql=data['sql'], share=data['share'], locked=data['locked'],
                                           created_by=data['user'], created_date=datetime.now(),
                                           target=selected_db,
                                           databases=dbs_list_str
                                           )
    except Exception as e:
        return_date["success"] = False
        return_date["error"] = str(e)
        print(str(e))
    return Response(return_date)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def quick_update_query(request):
    return_date = {"success": True}
    try:
        if request.method == 'POST':
            data = json.loads(request.POST.get('my_json_data'))
            if 'login_user' in data:
                login_user = data['login_user']
                login_user_is_staff = User.objects.get(username=login_user).is_superuser
            else:
                login_user = request.user
                login_user_is_staff = request.user.is_superuser
            find_query = QueryScript.objects.filter(id=data['id'])
            if find_query.exists():
                if str(find_query[0].created_by) == str(login_user) or login_user_is_staff:
                    find_query.update(sql=data['sql'])
                else:
                    raise Exception("You can't update query that own by others.")
            else:
                raise Exception("Can't find query by given id: %s. This query maybe does not exists." % data['id'])

    except Exception as e:
        return_date["success"] = False
        return_date["error"] = str(e)
        print(str(e))
    return Response(return_date)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def load_query(request):
    query_data = {}

    try:
        if request.method == 'POST':
            data = json.loads(request.POST.get('my_json_data'))
            query = QueryScript.objects.get(id=data['id'])
            if query:
                query_data["name"] = query.name
                query_data["description"] = query.description
                query_data["category"] = query.category
                query_data["sql"] = query.sql
                query_data["databases"] = query.databases
                query_data["target"] = query.target
                query_data["owner"] = query.created_by
                query_data["locked"] = query.locked
                query_data["share"] = query.share
    except Exception as e:
        query_data = {}
    return Response(query_data)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def delete_query(request):
    return_date = {"success": True}
    try:
        if request.method == 'POST':
            data = json.loads(request.POST.get('my_json_data'))
            if 'login_user' in data:
                login_user = data['login_user']
                login_user_is_staff = User.objects.get(username=login_user).is_superuser
            else:
                login_user = request.user
                login_user_is_staff = request.user.is_superuser

            query = QueryScript.objects.get(id=data['id'])
            if str(query.created_by) == str(login_user) or login_user_is_staff:
                query.delete()
            else:
                raise Exception("You can't delete query that own by others.")
    except Exception as e:
        return_date["success"] = False
        return_date['error'] = str(e)

    return Response(return_date)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def load_database_by_target(request):
    return_date = {"success": True, "target_server": ""}
    try:
        if request.method == 'POST':
            selected_db = request.POST.get('database')
            return_date['target_server'] = get_databases_by_name_endswith(selected_db)

    except Exception as e:
        return_date["success"] = False
        return_date["error"] = str(e)
    return Response(return_date)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_permission(request):
    return_date = {"success": True}
    try:
        if request.method == 'POST':
            data = json.loads(request.POST.get('my_json_data'))
            query = QueryScript.objects.get(id=data['id'])
            query.delete()
    except Exception as e:
        return_date["success"] = False
        return_date['error'] = str(e)

    return Response(return_date)


# Common method
def get_object_value(obj, field_name):
    field_object = obj._meta.get_field(field_name)
    return field_object.value_from_object(obj)


def get_databases_by_name_endswith(db_name):
    dbs_list = []
    db_instances = Database.objects.filter(name__endswith=str(db_name))
    for db in db_instances:
        db_json = {'id': db.id, 'name': db.name}
        dbs_list.append(db_json)
    return dbs_list

