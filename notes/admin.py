from django.contrib import admin
from .models import Note, ToDoNote, ToDo

admin.site.register(Note)
admin.site.register(ToDoNote)
admin.site.register(ToDo)
