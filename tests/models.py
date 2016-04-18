from django.db import models

class Parent(models.Model):
    char_field = models.CharField(max_length = 50, default = 'Parent CharField contents.')

class Child(models.Model):
    char_field = models.CharField(max_length=50, default = 'Child CharField contents.', unique=True)
    text_field = models.TextField(default = 'Child TextField contents.')
    decimal_field = models.DecimalField(max_digits=20, decimal_places=3, default=3.434)
    date_field = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('Parent')

    def natural_key(self):
        return (self.char_field)



