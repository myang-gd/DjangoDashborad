from django.contrib import admin

# Register your models here.
from apps.query_view.models import QueryScript, Database, UserProfile, Favorite, Recent, ExecuteHistory

admin.site.register(QueryScript)
admin.site.register(Database)
admin.site.register(UserProfile)
admin.site.register(Favorite)
admin.site.register(Recent)
admin.site.register(ExecuteHistory)