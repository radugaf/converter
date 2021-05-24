from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

PRODUCT_NAME = (
    ("Product-A", "Product A"),
    ("Product-B", "Product B"),
    ("Product-C", "Product C"),
)


class Data(models.Model):
    title = MultiSelectField(max_length=100, blank=True, null=True, choices=PRODUCT_NAME)
    delivery_date = models.DateField()
    quantity = models.IntegerField(default=1)

    # Helpers
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

