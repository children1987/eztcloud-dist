from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0071_fixedproduct_code_deversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixedproductversion',
            name='publish_time',
            field=models.DateTimeField(
                verbose_name='发布时间',
                help_text='发布时间（版本首次发布的时间）',
                null=True,
                blank=True,
            ),
        ),
    ]


