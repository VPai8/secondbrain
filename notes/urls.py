from django.urls import path
from .views import *
urlpatterns = [
    path('notes/', Home.as_view(), name='notes-home'),

    path('notes/create/', NotesCreateView.as_view(), name='notes-create'),
    path('notes/<int:pk>/update', NotesUpdateView.as_view(), name='notes-update'),
    path('notes/<int:pk>/delete', NotesDeleteView.as_view(), name='notes-delete'),
    path('notes/<int:id>/pin', pin_note, name='notes-pin'),

    path('notes/td/create',
         ToDoNotesCreateView.as_view(), name='tdnotes-create'),
    path('notes/td/<int:pk>/update',
         ToDoNotesUpdateView.as_view(), name='tdnotes-update'),
    path('notes/td/<int:pk>/delete',
         ToDoNotesDeleteView.as_view(), name='tdnotes-delete'),
    path('notes/td/<int:id>/pin', pin_tdnote, name='tdnotes-pin'),

    path('notes/td/<int:id>',
         item_list, name='notes-itemlist'),
    path('notes/td/<int:pk>/add-todo/',
         ToDoCreateView.as_view(), name='notes-todo'),
    path('notes/td/item/<int:id>/update',
         item_update, name='notes-itemupdate'),
    path('notes/td/item/<int:id>/delete',
         item_delete, name='notes-itemdelete'),
    path('notes/td/item/<int:id>/check',
         item_check, name='notes-itemcheck'),

    path('about/', about, name='notes-about'),
]
