from django.db import models

class Session(models.Model):

    created_at = models.DecimalField(max_digits=13, decimal_places=3)
    session_id = models.TextField(primary_key=True)
    last_renewed = models.DecimalField(max_digits=13, decimal_places=3)


class Message(models.Model):

    id = models.TextField(primary_key=True)
    session = models.ForeignKey(Session, default=None, on_delete=models.PROTECT)
    sender_id = models.TextField()
    recipient_id = models.TextField()
    timestamp = models.DecimalField(max_digits=13, decimal_places=3)
    text = models.TextField()


class Hobby(models.Model):

    created_at = models.DecimalField(max_digits=13, decimal_places=3)
    user = models.TextField()
    hobby = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'hobby'], name='one_of_each_hobby')
        ]
