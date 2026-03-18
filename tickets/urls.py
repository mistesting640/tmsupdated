from django.urls import path
from . import views
app_name = 'tickets'
urlpatterns = [

path('',views.dashboard,name='dashboard'),
path('create/',views.create_ticket,name="create_ticket"),
path('ticket/<int:id>/', views.ticket_detail, name='ticket_detail'),
path('register/', views.register_view, name='register'),
path('agent-queue/', views.agent_queue, name='agent_queue'),
path('assign/<int:ticket_id>/', views.assign_ticket, name='assign_ticket'),
path('my-tickets/', views.my_tickets, name='my_tickets'),
path('my-assigned/', views.my_assigned, name='my_assigned'),
path('logout/', views.custom_logout, name='logout'),
path('edit/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
path('delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
path('update-status/<int:ticket_id>/', views.update_status, name='update_status'),
]