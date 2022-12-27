# Generated by Django 3.2.16 on 2022-12-25 09:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(help_text='Имена авторов, на которых подписан', on_delete=django.db.models.deletion.CASCADE, related_name='is_subscribed', to=settings.AUTH_USER_MODEL, verbose_name='На кого подписан')),
                ('subscriber', models.ForeignKey(help_text='Кто подписан', on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
        ),
    ]
