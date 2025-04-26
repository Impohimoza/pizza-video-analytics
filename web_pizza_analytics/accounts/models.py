from django.contrib.auth.models import AbstractUser
from django.db import models
from evaluateRegister.models import PizzeriaLocation


class CustomUser(AbstractUser):
    pizzeria_location = models.ForeignKey(PizzeriaLocation, on_delete=models.SET_NULL, null=True, blank=True)

    def is_manager(self):
        return self.groups.filter(name="Менеджеры пиццерий").exists()

    def is_admin(self):
        return self.is_superuser or self.groups.filter(name="Администраторы сети").exists()
