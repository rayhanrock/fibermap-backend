from django.contrib import admin
from .models import Cable, Marker, Core, POP, Junction, Client, Gpon

admin.site.register(Marker)

admin.site.register(POP)
admin.site.register(Client)
admin.site.register(Junction)
admin.site.register(Gpon)
admin.site.register(Cable)
admin.site.register(Core)