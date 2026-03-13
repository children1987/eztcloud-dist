from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_servers', '0019_alter_clientdomain_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='we_svc_name',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='微信服务号 名称'),
        ),
    ]
