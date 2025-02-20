from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic import CreateView, TemplateView, ListView, DetailView, DeleteView, UpdateView, FormView

from .models import Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from agents.mixins import OrganizerAndLoginRequiredMixin

class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    
    def get_success_url(self):
        return reverse("login")

class LandingPageView(TemplateView):
    template_name = "landing.html"

def landing_page(request):
    return render(request, "landing.html")

class LeadListView(LoginRequiredMixin, ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    
    def get_queryset(self):
        user = self.request.user        
        #initial queryset of all the leads for the entire organization
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)            
            #filtering for the agent currently logged in
            queryset = queryset.filter(agent__user=self.request.user)        
        return queryset 
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, 
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads": leads
    }
    return render(request, 'leads/lead_list.html', context)

class LeadDetailView(LoginRequiredMixin,DetailView):
    template_name = "leads/lead_detail.html"
    queryset = Lead.objects.all()
    context_object_name = "lead"
    
    

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    return render(request, "leads/lead_detail.html", context)

class LeadCreateView(OrganizerAndLoginRequiredMixin,CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created.", 
            message="Visit the site to check it out.",
            from_email="test_sender@test.com",
            recipient_list=["test_recipient@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)

def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)        
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        'form': form
    }
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganizerAndLoginRequiredMixin, UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm 
       
    def get_queryset(self):
        user = self.request.user        
        #initial queryset of all the leads for the entire organization       
        return Lead.objects.filter(organization=user.userprofile)
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def get_queryset(self):
        return Lead.objects.all()

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)        
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        'form': form,
        "lead": lead,
    }
    return render(request, "leads/lead_update.html", context)

class LeadDeleteView(OrganizerAndLoginRequiredMixin,DeleteView):
    template_name = "leads/lead_delete.html"
    
    def get_success_url(self):        
        return reverse("leads:lead-list")
    
    def get_queryset(self):
        user = self.request.user        
        #initial queryset of all the leads for the entire organization       
        return Lead.objects.filter(organization=user.userprofile)

def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")

class AssignAgentView(OrganizerAndLoginRequiredMixin, FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update( {
            "request": self.request
        })
        return kwargs
    
    def get_success_url(self):        
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
    
class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"
    
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        context.update({
            "unassigned_lead_count": Lead.objects.filter(category__isnull=True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)            
        return queryset
    
class CategoryDetailView(LoginRequiredMixin, DetailView):
    template_name= "leads/category_detail.html"
    context_object_name = "category"
    
    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)
    #     leads = self.get_object().leads.all()
        
    #     context.update({
    #         "leads": leads 
    #     })
    #     return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)            
        return queryset
    
class LeadCategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm 
       
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_organizer:
    #         queryset = Lead.objects.filter(organization=user.userprofile)
    #     else:
    #         queryset = Lead.objects.filter(organization=user.agent.organization)            
    #         #filtering for the agent currently logged in
    #         queryset = queryset.filter(agent__user=user)
    #     return queryset
    
    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})
    
    def get_queryset(self):
        return Lead.objects.all()