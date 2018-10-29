# Generated by Django 2.0.1 on 2018-10-28 18:57

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pybb', '0009_remove_forum_subscribers'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bump',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=85)),
                ('note', models.CharField(blank=True, max_length=200)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('forum', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='pybb.Forum')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claims', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClaimLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
            ],
        ),
        migrations.CreateModel(
            name='ClaimLinkType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=35)),
                ('forward_name', models.CharField(max_length=35)),
                ('reverse_name', models.CharField(max_length=35)),
                ('is_directional', models.BooleanField(default=True)),
                ('is_recursive', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.IntegerField(validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(1)])),
                ('claim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='engage.Claim')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='claimlink',
            name='link_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='engage.ClaimLinkType'),
        ),
        migrations.AddField(
            model_name='claimlink',
            name='linked_claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='super_links', to='engage.Claim'),
        ),
        migrations.AddField(
            model_name='claimlink',
            name='primary_claim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_links', to='engage.Claim'),
        ),
        migrations.AddField(
            model_name='claimlink',
            name='topic',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='link', to='pybb.Topic'),
        ),
        migrations.AddField(
            model_name='claimlink',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bump',
            name='claimlink',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bumps', to='engage.ClaimLink'),
        ),
        migrations.AddField(
            model_name='bump',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bumps', to=settings.AUTH_USER_MODEL),
        ),
    ]
