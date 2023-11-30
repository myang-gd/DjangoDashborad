from django.http import HttpResponse
# Create your views here.
from django.views.generic import TemplateView

from apps.query_view.models import QueryScript, DatabaseName, CategoryName, TargetDatabasesMapping


class QuerySplitterView(TemplateView):
    template_name = "query_view_splitter.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['login_user'] = str(request.user)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class QueryView(TemplateView):
    template_name = "query_view.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['login_user'] = str(request.user)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RegisterView(TemplateView):
    template_name = "register_view.html"

    def get(self, request, *args, **kwargs):
        copy_from_id = request.GET.get('copy_from_id', r'')
        context = self.get_context_data(**kwargs)
        context['login_user'] = str(request.user)

        target_list = list(set(DatabaseName.objects.values_list('dbName', flat=True)))
        category_list = list(set(CategoryName.objects.values_list('category', flat=True)))
        target_list.sort()
        category_list.sort()

        context['target_list'] = target_list
        context['script_data'] = {'name': '', 'description': '', 'sql': '', 'category': '', 'target': target_list[0],
                                  'share': True, 'locked': False, 'databases': '', 'created_by': request.user}
        context['category_list'] = category_list

        if copy_from_id:
            query_find = QueryScript.objects.filter(id=copy_from_id)
            if query_find.exists():
                query = query_find[0]
                context['script_data']['name'] = query.name + " - Copy "
                context['script_data']['description'] = query.description
                context['script_data']['category'] = query.category
                context['script_data']['sql'] = query.sql
                context['script_data']['target'] = query.target
                context['script_data']['share'] = query.share
                context['script_data']['databases'] = query.databases

        return self.render_to_response(context)


class EditView(TemplateView):
    template_name = "edit_view.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['login_user'] = str(request.user)
        try:
            target_list = list(set(DatabaseName.objects.values_list('dbName', flat=True)))
            category_list = list(set(CategoryName.objects.values_list('category', flat=True)))
            target_list.sort()
            category_list.sort()

            query_id = request.GET['id']
            query = QueryScript.objects.get(id=query_id)
            if not request.user.is_superuser and str(request.user) != str(query.created_by):
                read_only = "true"
            else:
                read_only = "false"
            context["query_id"] = query_id
            context["target_list"] = target_list
            context["category_list"] = category_list
            context["read_only"] = read_only

        except Exception as ex:
            return HttpResponse(str(ex), status=400)

        return self.render_to_response(context)

