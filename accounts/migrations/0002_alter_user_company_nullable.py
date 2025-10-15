from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="company",
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                verbose_name="Entreprise",
            ),
        ),
    ]
