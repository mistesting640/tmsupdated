from django.db import models
from django.contrib.auth.models import User

PRIORITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Critical', 'Critical'),
]

STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Pending', 'Pending'),
    ('Closed', 'Closed'),
]

class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    # 🔥 NEW FIELDS
    department = models.CharField(max_length=100, default="General")
    project = models.CharField(max_length=100, default="General")

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 SLA FIELD
    sla_deadline = models.DateTimeField(null=True, blank=True)

    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')

    def __str__(self):
        return self.title

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user}"