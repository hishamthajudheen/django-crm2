import random
from django.shortcuts import render
from django.shortcuts import reverse, redirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView


from .forms import AgentModelForm
from leads.models import Agent, UserProfile
from .mixins import OrganizerAndLoginRequiredMixin


class AgentListView(OrganizerAndLoginRequiredMixin, ListView):
    template_name = "agents/agent_list.html"
    context_object_name = "agents"
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    
class AgentCreateView(OrganizerAndLoginRequiredMixin, CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm
    
    def get_success_url(self):
        return reverse("agents:agent-list")
    
    def form_valid(self, form):        
        # userprofile, created = UserProfile.objects.get_or_create(user=self.request.user)
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organizer = False
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        send_mail(
            subject = "You are invited as an Agent",
            message= "You were added as an agent on Django CRM 2. Please login to start working.",
            from_email="admin@email.com",
            recipient_list=[user.email]
        )
        return super(AgentCreateView, self).form_valid(form)
    
class AgentDetailView(OrganizerAndLoginRequiredMixin, DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    
class AgentUpdateView(OrganizerAndLoginRequiredMixin, UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm    
    context_object_name = "agent"
    
    def get_success_url(self):
        return reverse("agents:agent-list")
    
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    
class AgentDeleteView(OrganizerAndLoginRequiredMixin,DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"
    
    def get_success_url(self):        
        return reverse("agents:agent-list")
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    