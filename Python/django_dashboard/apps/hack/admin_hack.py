from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType 
from django.contrib.admin.templatetags.admin_modify import register
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row
from django.db.models.signals import post_migrate
def add_view_permission(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission to all our
    content types.
    """
    for content_type in ContentType.objects.all():
        codename = "view_only_%s" % content_type.model
 
        if not Permission.objects.filter(content_type=content_type, codename=codename):
            Permission.objects.create(
                content_type=content_type,
                codename=codename,
                name="Can only view %s" % content_type.name
            )
 
post_migrate.connect(add_view_permission)
 
class HackAdminModel(admin.ModelAdmin):
    @register.inclusion_tag('admin/submit_line.html', takes_context=True)
    def submit_row(context):
        """Sumbit row.
  
        :param context: Dictionary of required data.
        :return: Return update context.
        """
        ctx = original_submit_row(context)
        INDEX = 3 
        
        if not (type(context.dicts) is list and len(context.dicts) > INDEX and 'opts' in context.dicts[INDEX] and 'change' in context.dicts[INDEX] and context.dicts[INDEX]['change']):
            return ctx
        app_name, seprator, model_name = str(context.dicts[INDEX]['opts']).partition('.')
        
        for permission in context['request'].user.get_all_permissions():
            head, sep, tail = permission.partition('.')
            perm = "view_only_%s" % (model_name)
            if str(perm) == str(tail):
                if context['request'].user.has_perm(str(permission)) and \
                        not context['request'].user.is_superuser:
                    ctx.update({
                        'show_save_and_add_another': False,
                        'show_save_and_continue': False,
                        'show_save': False,
                    })
                return ctx
        return ctx


