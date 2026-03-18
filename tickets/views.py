
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import Group
from django.db.models import Q
from django.contrib import messages
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm, RegisterForm
from datetime import timedelta
from django.utils import timezone

@login_required
def dashboard(request):
    user = request.user

    # ✅ ADMIN FIX (ADD THIS)
    if user.is_superuser:
        role = "manager"
        tickets = Ticket.objects.all()

    elif user.groups.filter(name='Customer').exists():
        role = "customer"
        tickets = Ticket.objects.filter(created_by=user)

    elif user.groups.filter(name='Support Agent').exists():
        role = "internal"
        tickets = Ticket.objects.all()

    elif user.groups.filter(name='Manager').exists():
        role = "manager"
        tickets = Ticket.objects.all()

    else:
        role = "unknown"
        tickets = Ticket.objects.none()

    # 🔍 Search
    search = request.GET.get('search')
    if search:
        tickets = tickets.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # 📊 Counts (fixed)
    open_count = tickets.filter(status="Open").count()
    pending_count = tickets.filter(status="Pending").count()
    closed_count = tickets.filter(status="Closed").count()

    # 📊 Priority
    low = tickets.filter(priority="Low").count()
    medium = tickets.filter(priority="Medium").count()
    high = tickets.filter(priority="High").count()
    critical = tickets.filter(priority="Critical").count()

    return render(request, "tickets/dashboard.html", {
        "tickets": tickets,
        "role": role,
        "open_count": open_count,
        "pending_count": pending_count,
        "closed_count": closed_count,
        "low": low,
        "medium": medium,
        "high": high,
        "critical": critical,
        "my_ticket_count": tickets.count(),
        "assigned_count": tickets.filter(assigned_to=user).count(),
        "unassigned_count": Ticket.objects.filter(assigned_to__isnull=True).count() if is_agent(user) else 0,
    })


@login_required
def create_ticket(request):

    form = TicketForm()

    if request.method == 'POST':
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            return redirect('tickets:dashboard')

    return render(request,'tickets/create_ticket.html',{'form':form})

@login_required
def ticket_detail(request, id):

    ticket = get_object_or_404(Ticket, id=id)
    comments = Comment.objects.filter(ticket=ticket)

    form = CommentForm()

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.user = request.user
            comment.save()

            return redirect('tickets:ticket_detail', id=id)

    context = {
        'ticket': ticket,
        'comments': comments,
        'form': form
    }

    return render(request,'tickets/ticket_detail.html',context)

# tickets/views.py


def custom_logout(request):
    logout(request)
    return redirect('/')           # or 'login' or wherever


def is_agent(user):
    return user.groups.filter(name='Support Agent').exists()

@login_required
@user_passes_test(is_agent, login_url='login')
def agent_dashboard(request):
    # only agents see this
    tickets = Ticket.objects.filter(assigned_to=request.user)
    return render(request, 'tickets/agent_dashboard.html', {'tickets': tickets})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # 🔥 Proper password hashing
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Assign Customer group
            group, created = Group.objects.get_or_create(name='Customer')
            user.groups.add(group)

            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.groups.filter(name='Customer').exists():
                return redirect('dashboard')

            elif user.groups.filter(name='Support Agent').exists():
                return redirect('dashboard')

            elif user.is_staff:
                return redirect('/admin/')

    return render(request, 'login.html')

@login_required
def agent_queue(request):
    if not request.user.groups.filter(name='Support Agent').exists():
        return redirect('dashboard')

    tickets = Ticket.objects.filter(assigned_to__isnull=True)

    return render(request, 'tickets/agent_queue.html', {
        'tickets': tickets
    })
@login_required
def assign_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user.groups.filter(name='Support Agent').exists():
        ticket.assigned_to = request.user
        ticket.status = "Pending"
        ticket.save()

    return redirect('tickets:agent_queue')

from django.contrib.auth.decorators import login_required
from .models import Ticket
from django.shortcuts import render

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(created_by=request.user)
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})

@login_required
def my_assigned(request):
    tickets = Ticket.objects.filter(assigned_to=request.user)

    return render(request, 'tickets/my_assigned.html', {
        'tickets': tickets
    })

def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully ✅")
    return redirect('/accounts/login/')

@login_required
def create_ticket(request):

    form = TicketForm()

    if request.method == 'POST':
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user

            # 🔥 SLA LOGIC
            if ticket.priority == "Low":
                ticket.sla_deadline = timezone.now() + timedelta(days=3)

            elif ticket.priority == "Medium":
                ticket.sla_deadline = timezone.now() + timedelta(days=2)

            elif ticket.priority == "High":
                ticket.sla_deadline = timezone.now() + timedelta(days=1)

            elif ticket.priority == "Critical":
                ticket.sla_deadline = timezone.now() + timedelta(hours=4)

            ticket.save()

            return redirect('tickets:dashboard')

    return render(request,'tickets/create_ticket.html',{'form':form})

@login_required
def edit_ticket(request, ticket_id):

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket.title = request.POST.get("title")
        ticket.description = request.POST.get("description")
        ticket.priority = request.POST.get("priority")

        # ✅ NEW
        status = request.POST.get("status")
        if status:
            ticket.status = status

        ticket.save()

        return redirect('tickets:dashboard')

    return redirect('tickets:dashboard')

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user != ticket.created_by:
        return redirect('tickets:dashboard')

    ticket.delete()
    return redirect('tickets:dashboard')

@login_required
def update_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status:  # ✅ safety check
            ticket.status = status
            ticket.save()
            messages.success(request, "Status updated successfully")
        else:
            messages.error(request, "Invalid status")

    return redirect('tickets:dashboard')  # ✅ FIXED (namespace added)