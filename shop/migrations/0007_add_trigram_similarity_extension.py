from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0006_alter_product_title'),
    ]
    operations = [TrigramExtension()]