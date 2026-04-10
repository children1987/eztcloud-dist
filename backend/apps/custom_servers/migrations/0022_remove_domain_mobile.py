from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("custom_servers", "0021_alter_clientdomain_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="domain",
            name="mobile",
        ),
    ]
