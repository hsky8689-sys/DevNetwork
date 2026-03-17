from datetime import datetime
from django.db import models
from users.models import User

class Message(models.Model):
    user = models.ForeignKey(User,
                    on_delete=models.CASCADE
                    ,related_name='messages'
                    )
    content = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(default='3000-10-10 ')
    image = models.ImageField(default='fallback.png',blank=True)

    class Meta:
        db_table='messages'

