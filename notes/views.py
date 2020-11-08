from django.shortcuts import render, Http404, redirect, get_object_or_404, get_list_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import *
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.urls import reverse_lazy, reverse
from itertools import chain
from operator import attrgetter
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q


class Home(LoginRequiredMixin, ListView):
    context_object_name = 'notes'
    template_name = 'notes/home.html'

    def get_queryset(self):
        squery = self.request.GET.get('search')
        print(squery)
        if squery == None or squery == "":
            notes = Note.objects.filter(
                user=self.request.user).order_by('-pin', '-last_edit').values()
            tdnotes = ToDoNote.objects.note_with_todos(user=self.request.user)
        else:
            filters = Q(user=self.request.user) & (
                Q(title__icontains=squery) | Q(note__icontains=squery))
            notes = Note.objects.filter(filters).order_by(
                '-pin', '-last_edit').values()
            tdnotes = ToDoNote.objects.note_with_todos(
                user=self.request.user, squery=squery)

        from itertools import chain
        from operator import itemgetter
        self.queryset = sorted(
            chain(notes, tdnotes),
            key=itemgetter('pin', 'last_edit'),
            reverse=True)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notes_left = [note for idx, note in enumerate(
            self.queryset) if idx % 2 == 0]
        notes_right = [note for idx, note in enumerate(
            self.queryset) if idx % 2 == 1]
        context['notes_left'] = notes_left
        context['notes_right'] = notes_right
        return context


class NotesCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Note
    fields = ['title', 'note', 'color', 'pin']
    success_url = reverse_lazy('notes-home')
    success_message = 'Note created!'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NotesUpdateView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = Note
    fields = ['title', 'note', 'color', 'pin']
    success_url = reverse_lazy('notes-home')
    template_name = 'notes/note_edit_form.html'
    success_message = 'Note updated!'

    def test_func(self):
        note = self.get_object()
        if self.request.user == note.user:
            return True
        return False


class NotesDeleteView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('notes-home')
    success_message = 'Note deleted!'

    def test_func(self):
        note = self.get_object()
        if self.request.user == note.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        data_to_return = super(NotesDeleteView, self).delete(
            request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return data_to_return


class ToDoNotesCreateView(LoginRequiredMixin, CreateView):
    model = ToDoNote
    fields = ['title', 'color', 'pin']
    template_name = 'notes/tdnote_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('notes-todo', args=(self.object.pk,))


class ToDoNotesUpdateView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = ToDoNote
    fields = ['title', 'color', 'pin']
    success_url = reverse_lazy('notes-home')
    template_name = 'notes/tdnote_edit_form.html'
    success_message = 'Note updated!'

    def test_func(self):
        tdnote = self.get_object()
        if self.request.user == tdnote.user:
            return True
        return False


class ToDoNotesDeleteView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, DeleteView):
    model = ToDoNote
    success_url = reverse_lazy('notes-home')
    success_message = 'Note deleted!'

    def test_func(self):
        tdnote = self.get_object()
        if self.request.user == tdnote.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        data_to_return = super(ToDoNotesDeleteView, self).delete(
            request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return data_to_return


class AjaxableResponseMixin(object):
    def form_valid(self, form):
        form.instance.note = ToDoNote.objects.get(pk=self.kwargs['pk'])
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            print('invalid loop')
            return JsonResponse(form.errors, status=400)
        else:
            return response


class ToDoCreateView(LoginRequiredMixin,  AjaxableResponseMixin, CreateView):
    model = ToDo
    fields = ['item']
    template_name = 'notes/todo.html'

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['noteid'] = self.kwargs['pk']
        return context


@login_required
def pin_note(request, id):
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=id)
        if note.user == request.user:
            note.pin ^= 1
            note.save()
            return JsonResponse({})
        else:
            raise PermissionDenied
    else:
        raise Http404()


@login_required
def pin_tdnote(request, id):
    if request.method == 'POST':
        note = get_object_or_404(ToDoNote, pk=id)
        if note.user == request.user:
            note.pin ^= 1
            note.save()
            return JsonResponse({})
        else:
            raise PermissionDenied
    else:
        raise Http404()


@login_required
def item_check(request, id):
    if request.method == 'POST':
        item = get_object_or_404(ToDo, pk=id)
        if item.note.user == request.user:
            item.completed ^= 1
            item.save()
            return JsonResponse({})
        else:
            raise PermissionDenied
    else:
        raise Http404()


@login_required
def item_delete(request, id):
    if request.method == 'POST':
        item = get_object_or_404(ToDo, pk=id)
        if item.note.user == request.user:
            item.delete()
            return JsonResponse({})
        else:
            raise PermissionDenied
    else:
        raise Http404()


@login_required
def item_list(request, id):
    tdnote = get_object_or_404(ToDoNote, pk=id)
    if tdnote.user == request.user:
        items = get_list_or_404(ToDo, note=tdnote)
        response = serializers.serialize("json", items)
        return HttpResponse(response, content_type='application/json')
    else:
        raise PermissionDenied


@login_required
def item_update(request, id):
    if request.method == 'POST':
        todo = get_object_or_404(ToDo, pk=id)
        if todo.note.user == request.user:
            todo.item = request.POST['item']
            todo.save()
            return JsonResponse({})
        else:
            raise PermissionDenied
    else:
        raise Http404()


@login_required
def about(request):
    return render(request, 'notes/about.html')
