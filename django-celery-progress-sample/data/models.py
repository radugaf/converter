from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

PRODUCT_NAME = (
    ("Product-A", "Product A"),
    ("Product-B", "Product B"),
    ("Product-C", "Product C"),
)

class FileInfo(models.Model):
    file = models.FileField()
    status = models.CharField(
        max_length=250,
        choices=(
            ('PENDING', 'PENDING'),
            ('PROCESSING', 'PROCESSING'),
            ('PROCESSED', 'PROCESSED'),
        ),
        default='PENDING'
    )

class Data(models.Model):
    file_info = models.ForeignKey(FileInfo, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    delivery_date = models.DateField()
    quantity = models.IntegerField(default=1)

    # Helpers
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

