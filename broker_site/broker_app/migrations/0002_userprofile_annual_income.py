# Generated by Django 5.0.7 on 2024-12-11 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='annual_income',
            field=models.CharField(choices=[('below_20k', 'Below $20,000'), ('20k_40k', '$20,000 - $40,000'), ('40k_60k', '$40,000 - $60,000'), ('60k_80k', '$60,000 - $80,000'), ('80k_100k', '$80,000 - $100,000'), ('100k_150k', '$100,000 - $150,000'), ('150k_above', 'Above $150,000')], default='below_20k', max_length=15, verbose_name='Annual Income'),
        ),
    ]
