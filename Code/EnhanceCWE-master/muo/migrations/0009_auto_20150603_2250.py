# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0008_auto_20150602_0054'),
    ]

    operations = [
        migrations.AddField(
            model_name='misusecase',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='osr',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='misusecase',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='misusecase',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='cwes',
            field=models.ManyToManyField(related_name='muo_container', to='cwe.CWE'),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='misuse_cases',
            field=models.ManyToManyField(related_name='muo_container', to='muo.MisuseCase'),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='osrs',
            field=models.ManyToManyField(related_name='muo_container', to='muo.OSR'),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='use_cases',
            field=models.ManyToManyField(related_name='muo_container', to='muo.UseCase'),
        ),
        migrations.AlterField(
            model_name='osr',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='osr',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
