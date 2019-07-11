from django.db import models

class Session(models.Model):
    created_at = models.DecimalField(max_digits=13, decimal_places=3)
    session_id = models.TextField()
    last_updated = models.DecimalField(max_digits=13, decimal_places=3)


class Message(models.Model):
    pass