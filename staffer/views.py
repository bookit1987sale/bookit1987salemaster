from random import randint

from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from staffer.models import StaffMember
from service.models import Service
from staffer.forms import SignUpStaffForm, StaffUpdateForm
from rest_framework import viewsets
from staffer.serializers import StaffMemberSerializer


class StaffUpdate(UpdateView):
    model = StaffMember
    success_message = "%(item)s was successfully updated"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = StaffUpdateForm

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update {}".format(
            self.object.get_friendly_name()
            )
        context['button'] = "Update"
        # context['company'] = get_object_or_404(Company, pk=1)
        return context


class StaffList(ListView):
    model = StaffMember
    template_name = "staff/staff_list.html"
    title = "All Staff"
    context_object_name = 'all_staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class SignupStaffView(FormView): #(PasswordMixin, FormView):

    template_name = "staff/signup.html"
    # template_name_ajax = "account/ajax/signup.html"
    # template_name_email_confirmation_sent = "account/email_confirmation_sent.html"
    # template_name_email_confirmation_sent_ajax = "account/ajax/email_confirmation_sent.html"
    # template_name_signup_closed = "account/signup_closed.html"
    # template_name_signup_closed_ajax = "account/ajax/signup_closed.html"
    form_class = SignUpStaffForm
    # form_kwargs = {}
    # form_password_field = "password"
    # redirect_field_name = "next"
    # identifier_field = "username"
    # messages = {
    #     "email_confirmation_sent": {
    #         "level": messages.INFO,
    #         "text": _("Confirmation email sent to {email}.")
    #     },
    #     "invalid_signup_code": {
    #         "level": messages.WARNING,
    #         "text": _("The code {code} is invalid.")
    #     }
    # }
    # fallback_url_setting = "ACCOUNT_SIGNUP_REDIRECT_URL"

    # def __init__(self, *args, **kwargs):
    #     self.created_user = None
    #     kwargs["signup_code"] = None
    #     super(SignupView, self).__init__(*args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        # self.setup_signup_code()
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    # def setup_signup_code(self):
    #     code = self.get_code()
    #     if code:
    #         try:
    #             self.signup_code = SignupCode.check_code(code)
    #         except SignupCode.InvalidCode:
    #             self.signup_code = None
    #         self.signup_code_present = True
    #     else:
    #         self.signup_code = None
    #         self.signup_code_present = False

    # def get(self, *args, **kwargs):
    #     if is_authenticated(self.request.user):
    #         return redirect(default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL))
    #     if not self.is_open():
    #         return self.closed()
    #     return super(SignupView, self).get(*args, **kwargs)

    # def post(self, *args, **kwargs):
    #     if is_authenticated(self.request.user):
    #         raise Http404()
    #     if not self.is_open():
    #         return self.closed()
    #     return super(SignupView, self).post(*args, **kwargs)

    def generate_initial_password(self):
        temp_password = 0
        while len(temp_password) <= 5:
            temp_password += randint(0, 9)
        return temp_password

    def get_initial(self):
        # initial = super(SignupView, self).get_initial()
        # if self.signup_code:
        initial["staff"] = True
        initial["initial_password"] = self.generate_initial_password()
        return initial

    # def get_template_names(self):
    #     if self.request.is_ajax():
    #         return [self.template_name_ajax]
    #     else:
    #         return [self.template_name]

    def get_form_kwargs(self):
        kwargs = super(SignupView, self).get_form_kwargs()
        kwargs.update(self.form_kwargs)
        return kwargs

    # def form_invalid(self, form):
    #     signals.user_sign_up_attempt.send(
    #         sender=SignupForm,
    #         username=get_form_data(form, self.identifier_field),
    #         email=get_form_data(form, "email"),
    #         result=form.is_valid()
    #     )
    #     return super(SignupView, self).form_invalid(form)

    def form_valid(self, form):
        self.created_user = self.create_user(form, commit=False)
        # prevent User post_save signal from creating an Account instance
        # we want to handle that ourself.
        self.created_user._disable_account_creation = True
        self.created_user.save()
        # self.use_signup_code(self.created_user)
        email_address = self.create_email_address(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            self.created_user.is_active = False
            self.created_user.save()
        self.staff_account = self.create_account(form)
        self.create_staff(form)
        self.create_password_history(form, self.created_user)
        self.after_signup(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL and not email_address.verified:
            self.send_email_confirmation(email_address)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            return self.email_confirmation_required_response()
        else:
            show_message = [
                settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL,
                self.messages.get("email_confirmation_sent"),
                not email_address.verified
            ]
            if all(show_message):
                messages.add_message(
                    self.request,
                    self.messages["email_confirmation_sent"]["level"],
                    self.messages["email_confirmation_sent"]["text"].format(**{
                        "email": form.cleaned_data["email"]
                    })
                )
            # attach form to self to maintain compatibility with login_user
            # API. this should only be relied on by d-u-a and it is not a stable
            # API for site developers.
            self.form = form
            # self.login_user()
        return redirect(self.get_success_url())

    def create_user(self, form, commit=True, model=None, **kwargs):
        User = model
        if User is None:
            User = get_user_model()
        user = User(**kwargs)
        user.username = self.generate_username(form)
        user.email = form.cleaned_data["email"].strip()
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.phone_number = form.cleaned_data["phone_number"]
        user.alt_phone_number = form.cleaned_data["alt_phone_number"]
        password = form.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

    def create_account(self, form):
        return Account.create(request=self.request, user=self.created_user, create_email=False)

    def generate_username(self, form):	
        return "{}{}.".format(
            form.cleaned_data["first_name"],
            sform.cleaned_data["last_name"][0]
        )

    def create_staff(self, form):
        staff = StaffMember(**kwargs)
        staff.base_account = self.staff_account
        staff.initial_password = form.cleaned_data["initial_password"]
        if form.cleaned_data["spouse_name"]:
        	staff.spouse_name = form.cleaned_data["spouse_name"]
        staff.street_address = form.cleaned_data["street_address"]
        staff.city = form.cleaned_data["city"]
        staff.state = form.cleaned_data["state"]
        staff.zip_code = form.cleaned_data["zip_code"]
        staff.save()
        return staff

    def create_email_address(self, form, **kwargs):
        kwargs.setdefault("primary", True)
        kwargs.setdefault("verified", False)
        if self.signup_code:
            kwargs["verified"] = self.created_user.email == self.signup_code.email if self.signup_code.email else False
        return EmailAddress.objects.add_email(self.created_user, self.created_user.email, **kwargs)

    # def use_signup_code(self, user):
    #     if self.signup_code:
    #         self.signup_code.use(user)

    # def send_email_confirmation(self, email_address):
    #     email_address.send_confirmation(site=get_current_site(self.request))

    # def after_signup(self, form):
    #     signals.user_signed_up.send(sender=SignupForm, user=self.created_user, form=form)

    # def login_user(self):
    #     user = auth.authenticate(**self.user_credentials())
    #     auth.login(self.request, user)
    #     self.request.session.set_expiry(0)

    # def user_credentials(self):
    #     return hookset.get_user_credentials(self.form, self.identifier_field)

    # def get_code(self):
    #     return self.request.POST.get("code", self.request.GET.get("code"))

    # def is_open(self):
    #     if self.signup_code:
    #         return True
    #     else:
    #         if self.signup_code_present:
    #             if self.messages.get("invalid_signup_code"):
    #                 messages.add_message(
    #                     self.request,
    #                     self.messages["invalid_signup_code"]["level"],
    #                     self.messages["invalid_signup_code"]["text"].format(**{
    #                         "code": self.get_code(),
    #                     })
    #                 )
    #     return settings.ACCOUNT_OPEN_SIGNUP

    # def email_confirmation_required_response(self):
    #     if self.request.is_ajax():
    #         template_name = self.template_name_email_confirmation_sent_ajax
    #     else:
    #         template_name = self.template_name_email_confirmation_sent
    #     response_kwargs = {
    #         "request": self.request,
    #         "template": template_name,
    #         "context": {
    #             "email": self.created_user.email,
    #             "success_url": self.get_success_url(),
    #         }
    #     }
    #     return self.response_class(**response_kwargs)

    # def closed(self):
    #     if self.request.is_ajax():
    #         template_name = self.template_name_signup_closed_ajax
    #     else:
    #         template_name = self.template_name_signup_closed
    #     response_kwargs = {
    #         "request": self.request,
    #         "template": template_name,
    #     }
    #     return self.response_class(**response_kwargs)


# class LoginView(FormView):

#     template_name = "account/login.html"
#     template_name_ajax = "account/ajax/login.html"
#     form_class = LoginUsernameForm
#     form_kwargs = {}
#     redirect_field_name = "next"

#     @method_decorator(sensitive_post_parameters())
#     @method_decorator(csrf_protect)
#     @method_decorator(never_cache)
#     def dispatch(self, *args, **kwargs):
#         return super(LoginView, self).dispatch(*args, **kwargs)

#     def get(self, *args, **kwargs):
#         if is_authenticated(self.request.user):
#             return redirect(self.get_success_url())
#         return super(LoginView, self).get(*args, **kwargs)

#     def get_template_names(self):
#         if self.request.is_ajax():
#             return [self.template_name_ajax]
#         else:
#             return [self.template_name]

#     def get_context_data(self, **kwargs):
#         ctx = super(LoginView, self).get_context_data(**kwargs)
#         redirect_field_name = self.get_redirect_field_name()
#         ctx.update({
#             "redirect_field_name": redirect_field_name,
#             "redirect_field_value": self.request.POST.get(redirect_field_name, self.request.GET.get(redirect_field_name, "")),
#         })
#         return ctx

#     def get_form_kwargs(self):
#         kwargs = super(LoginView, self).get_form_kwargs()
#         kwargs.update(self.form_kwargs)
#         return kwargs

#     def form_invalid(self, form):
#         signals.user_login_attempt.send(
#             sender=LoginView,
#             username=get_form_data(form, form.identifier_field),
#             result=form.is_valid()
#         )
#         return super(LoginView, self).form_invalid(form)

#     def form_valid(self, form):
#         self.login_user(form)
#         self.after_login(form)
#         return redirect(self.get_success_url())

#     def after_login(self, form):
#         signals.user_logged_in.send(sender=LoginView, user=form.user, form=form)

#     def get_success_url(self, fallback_url=None, **kwargs):
#         if fallback_url is None:
#             fallback_url = settings.ACCOUNT_LOGIN_REDIRECT_URL
#         kwargs.setdefault("redirect_field_name", self.get_redirect_field_name())
#         return default_redirect(self.request, fallback_url, **kwargs)

#     def get_redirect_field_name(self):
#         return self.redirect_field_name

#     def login_user(self, form):
#         auth.login(self.request, form.user)
#         expiry = settings.ACCOUNT_REMEMBER_ME_EXPIRY if form.cleaned_data.get("remember") else 0
#         self.request.session.set_expiry(expiry)



class StaffMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = StaffMember.objects.filter(base_account__user__is_active=True)
    serializer_class = StaffMemberSerializer


    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     poss_staff= []
    #     params = self.request.query_params
    #     service = get(Service, pk=params['activity_pk'])
    #     for staff in queryset:
    #         for skill in staff.skill_set.all():
    #             if service == skill:
    #                 poss_staff.append(staff)
    #                 break
    #     return poss_staff

