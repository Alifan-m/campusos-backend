from django.db import models


class MapLocation(models.Model):
    TYPE_CHOICES = [
        ('cafeteria', 'Cafeteria'),
        ('library', 'Library'),
        ('lecture_hall', 'Lecture Hall'),
        ('admin', 'Administration'),
        ('hostel', 'Hostel'),
        ('sports', 'Sports'),
        ('clinic', 'Clinic'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150)
    location_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    description = models.TextField(blank=True)
    location_x = models.FloatField(help_text='X position as percentage (0.0 to 1.0)')
    location_y = models.FloatField(help_text='Y position as percentage (0.0 to 1.0)')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.location_type})"
