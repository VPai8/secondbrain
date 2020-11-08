from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Note(models.Model):
    class ColorPalette(models.TextChoices):
        Red = 'bg-danger'
        White = 'bg-light'
        Blue = 'bg-info'
        Green = 'bg-success'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    note = models.TextField()
    last_edit = models.DateTimeField(auto_now=True)
    color = models.CharField(choices=ColorPalette.choices,
                             default=ColorPalette.White, max_length=20)
    pin = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class TodoNoteManager(models.Manager):
    def note_with_todos(self, **kwargs):
        q = super().get_queryset().filter(user=kwargs['user'])
        if "squery" in kwargs:
            squery = kwargs['squery']
            filters = Q(title__icontains=squery) | Q(
                todo__item__icontains=squery)
            q = q.filter(filters).distinct()
            print(q)
        qv = q.values()
        for tdn, tdnv in zip(q.iterator(), qv):
            tdnv['todos'] = tdn.todo_set.all()[:10].values()
        return qv


class ToDoNote(models.Model):
    class ColorPalette(models.TextChoices):
        Red = 'bg-danger'
        White = 'bg-light'
        Blue = 'bg-info'
        Green = 'bg-success'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    last_edit = models.DateTimeField(auto_now=True)
    color = models.CharField(choices=ColorPalette.choices,
                             default=ColorPalette.White, max_length=20)
    pin = models.BooleanField(default=False)
    objects = TodoNoteManager()

    def __str__(self):
        return self.title


class ToDo(models.Model):
    note = models.ForeignKey(ToDoNote, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['completed', '-pk']

    def __str__(self):
        return self.item
