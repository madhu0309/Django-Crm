from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView, TemplateView, View, DeleteView)

from cases.models import Case
from cases.forms import CaseForm, CaseCommentForm
from common.models import Team, User, Comment
from accounts.models import Account
from contacts.models import Contact
from common.utils import PRIORITY_CHOICE, STATUS_CHOICE, CASE_TYPE


class CasesListView(LoginRequiredMixin, TemplateView):
    model = Case
    context_object_name = "cases"
    template_name = "cases.html"

    def get_queryset(self):
        queryset = self.model.objects.all().select_related("account")
        request_post = self.request.POST
        if request_post:
            if request_post.get('name'):
                queryset = queryset.filter(name__icontains=request_post.get('name'))
            if request_post.get('account'):
                queryset = queryset.filter(account_id=request_post.get('account'))
            if request_post.get('status'):
                queryset = queryset.filter(status=request_post.get('status'))
            if request_post.get('priority'):
                queryset = queryset.filter(priority=request_post.get('priority'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CasesListView, self).get_context_data(**kwargs)
        context["cases"] = self.get_queryset()
        context["accounts"] = Account.objects.all()
        context["per_page"] = self.request.POST.get('per_page')
        context["acc"] = int(self.request.POST.get("account")) if self.request.POST.get("account") else None
        context["case_priority"] = PRIORITY_CHOICE
        context["case_status"] = STATUS_CHOICE
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateCaseView(LoginRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = "create_cases.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        self.accounts = Account.objects.all()
        self.contacts = Contact.objects.all()
        return super(CreateCaseView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateCaseView, self).get_form_kwargs()
        kwargs.update({"assigned_to": self.users, "account": self.accounts,
                       "contacts": self.contacts})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        case = form.save(commit=False)
        case.created_by = self.request.user
        case.save()
        if self.request.POST.getlist('assigned_to', []):
            case.assigned_to.add(*self.request.POST.getlist('assigned_to'))
        if self.request.POST.getlist('teams', []):
            case.teams.add(*self.request.POST.getlist('teams'))
        if self.request.POST.getlist('contacts', []):
            case.contacts.add(*self.request.POST.getlist('contacts'))
        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("cases:add_case")
        else:
            return redirect('cases:list')

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'case_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CreateCaseView, self).get_context_data(**kwargs)
        context["teams"] = Team.objects.all()
        context["case_form"] = context["form"]
        context["accounts"] = self.accounts
        context["contacts"] = self.contacts
        context["users"] = self.users
        context["case_types"] = CASE_TYPE
        context["case_priority"] = PRIORITY_CHOICE
        context["case_status"] = STATUS_CHOICE
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        context["contacts_list"] = [
            int(i) for i in self.request.POST.getlist('contacts', []) if i]
        return context


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case
    context_object_name = "case_record"
    template_name = "view_case.html"

    def get_queryset(self):
        queryset = super(CaseDetailView, self).get_queryset()
        return queryset.prefetch_related("contacts", "account")

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context.update({"comments": context["case_record"].cases.all()})
        return context


class UpdateCaseView(LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = "create_cases.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        self.accounts = Account.objects.all()
        self.contacts = Contact.objects.all()
        return super(UpdateCaseView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateCaseView, self).get_form_kwargs()
        kwargs.update({"assigned_to": self.users, "account": self.accounts,
                       "contacts": self.contacts})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        case_obj = form.save()
        case_obj.assigned_to.clear()
        case_obj.teams.clear()
        case_obj.contacts.clear()
        if self.request.POST.getlist('assigned_to', []):
            case_obj.assigned_to.add(*self.request.POST.getlist('assigned_to'))
        if self.request.POST.getlist('teams', []):
            case_obj.teams.add(*self.request.POST.getlist('teams'))
        if self.request.POST.getlist('contacts', []):
            case_obj.contacts.add(*self.request.POST.getlist('contacts'))
        if self.request.is_ajax():
            return JsonResponse({'error': False})
        return redirect("cases:list")

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'case_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(UpdateCaseView, self).get_context_data(**kwargs)
        context["case_obj"] = self.object
        context["teams"] = Team.objects.all()
        context["case_form"] = context["form"]
        context["accounts"] = self.accounts
        context["contacts"] = self.contacts
        context["users"] = self.users
        context["case_types"] = CASE_TYPE
        context["case_priority"] = PRIORITY_CHOICE
        context["case_status"] = STATUS_CHOICE
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        context["contacts_list"] = [
            int(i) for i in self.request.POST.getlist('contacts', []) if i]
        return context


@login_required
def remove_case(request, case_id):
    if request.method == 'POST':
        get_object_or_404(Case, id=case_id).delete()
        if request.is_ajax():
            return JsonResponse({'error': False})
        count = Case.objects.filter(Q(assigned_to=request.user) | Q(created_by=request.user)).count()
        data = {"case_id": case_id, "count": count}
        return JsonResponse(data)
    else:
        Case.objects.filter(id=case_id).delete()
        return HttpResponseRedirect(reverse('cases:list'))


@login_required
def close_case(request):
    cid = request.POST['case_id']
    case = get_object_or_404(Case, id=cid)
    case.status = "Closed"
    case.save()
    data = {'status': "Closed", "cid": cid}
    return JsonResponse(data)


def selectContacts(request):
    contact_account = request.GET.get("account")
    if contact_account:
        account = get_object_or_404(Account, id=contact_account)
        contacts = Contact.objects.filter(account=account)
    else:
        contacts = Contact.objects.all()
    data = {}
    for i in contacts:
        new = {i.pk: i.first_name}
        data.update(new)
    return JsonResponse(data)


# CRUD Operations End
# Comments Section Start


@login_required
def add_comment(request):
    if request.method == 'POST':
        case = get_object_or_404(Case, id=request.POST.get('caseid'))
        if request.user in case.assigned_to.all() or request.user == case.created_by:
            form = CaseCommentForm(request.POST)
            if form.is_valid():
                case_comment = form.save(commit=False)
                case_comment.comment = request.POST.get('comment')
                case_comment.commented_by = request.user
                case_comment.case = case
                case_comment.save()
                data = {"comment_id": case_comment.id, "comment": case_comment.comment,
                        "commented_on": case_comment.commented_on,
                        "commented_by": case_comment.commented_by.email}
                return JsonResponse(data)
            else:
                return JsonResponse({"error": form['comment'].errors})
        else:
            data = {'error': "You Dont Have permissions to Comment"}
            return JsonResponse(data)


@login_required
def edit_comment(request):
    if request.method == "POST":
        comment = request.POST.get('comment')
        comment_id = request.POST.get("commentid")
        comment_obj = get_object_or_404(Comment, id=comment_id)
        form = CaseCommentForm(request.POST)
        if request.user == comment_obj.commented_by:
            if form.is_valid():
                comment_obj.comment = comment
                comment_obj.save()
                data = {"comment": comment_obj.comment, "commentid": comment_id}
                return JsonResponse(data)
            else:
                return JsonResponse({"error": form['comment'].errors})
        else:
            return JsonResponse({"error": "You dont have authentication to edit"})
    else:
        return render(request, "404.html")


@login_required
def remove_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.commented_by:
            comment.delete()
            data = {"cid": comment_id}
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "You Dont have permisions to delete"})
    else:
        return HttpResponse("Something Went Wrong")


# Comments Section End
# Other Views


@login_required
def get_cases(request):
    if request.method == 'GET':
        cases = Case.objects.all()
        return render(request, 'cases_list.html', {'cases': cases})
    else:
        return HttpResponse('Oops!! Something Went Wrong..  in load_calls')
