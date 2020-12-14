# Generated by Django 2.2.13 on 2020-12-14 12:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.migrations.operations.special
import django.db.models.deletion
import django_enumfield.db.fields
import surf.apps.communities.models
import surf.statusenums
import uuid


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# surf.apps.communities.migrations.0004_create_surf_teams

class Migration(migrations.Migration):

    replaces = [('communities', '0001_initial'), ('communities', '0002_community_collections'), ('communities', '0003_auto_20181210_1031'), ('communities', '0004_create_surf_teams'), ('communities', '0005_auto_20181210_1121'), ('communities', '0006_auto_20190801_1438'), ('communities', '0007_auto_20190806_1428'), ('communities', '0008_auto_20191104_1008'), ('communities', '0009_community_cleanup'), ('communities', '0010_auto_20200214_1051'), ('communities', '0011_update_meta_communities'), ('communities', '0012_auto_20200714_1324'), ('communities', '0013_update_title_fields')]

    initial = True

    dependencies = [
        ('locale', '0004_improved_translations'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materials', '0001_squashed_0028_collectionmaterial_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurfTeam',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(max_length=255, verbose_name='SURFconext group id')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('admins', models.ManyToManyField(blank=True, related_name='admin_teams', to=settings.AUTH_USER_MODEL, verbose_name='Administrators')),
                ('members', models.ManyToManyField(blank=True, related_name='teams', to=settings.AUTH_USER_MODEL, verbose_name='Members')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(max_length=255, verbose_name='SurfConext group id')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='communities')),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to='communities')),
                ('website_url', models.URLField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True, verbose_name='Is community available in service')),
                ('admins', models.ManyToManyField(blank=True, related_name='admin_communities', to=settings.AUTH_USER_MODEL, verbose_name='Administrators')),
                ('members', models.ManyToManyField(blank=True, related_name='communities', to=settings.AUTH_USER_MODEL, verbose_name='Members')),
                ('collections', models.ManyToManyField(blank=True, related_name='communities', to='materials.Collection')),
                ('surf_team', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community', to='communities.SurfTeam')),
            ],
            options={
                'verbose_name_plural': 'Communities',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='community',
            name='external_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='SurfConext group id'),
        ),
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RemoveField(
            model_name='community',
            name='featured_image',
        ),
        migrations.RemoveField(
            model_name='community',
            name='logo',
        ),
        migrations.AddField(
            model_name='community',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='community',
            name='publish_status',
            field=django_enumfield.db.fields.EnumField(default=0, enum=surf.statusenums.PublishStatus),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.CharField(blank=True, max_length=255)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Member',
            },
        ),
        migrations.AddField(
            model_name='community',
            name='new_members',
            field=models.ManyToManyField(blank=True, through='communities.Team', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='community',
            name='admins',
        ),
        migrations.RemoveField(
            model_name='community',
            name='is_available',
        ),
        migrations.RemoveField(
            model_name='community',
            name='members',
        ),
        migrations.RemoveField(
            model_name='community',
            name='surf_team',
        ),
        migrations.DeleteModel(
            name='SurfTeam',
        ),
        migrations.RenameField(
            model_name='community',
            old_name='new_members',
            new_name='members',
        ),
        migrations.RemoveField(
            model_name='community',
            name='description',
        ),
        migrations.RemoveField(
            model_name='community',
            name='website_url',
        ),
        migrations.CreateModel(
            name='CommunityDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=2)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=16384, null=True)),
                ('website_url', models.URLField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, help_text='The proportion of the image should be 230x136', null=True, upload_to='communities')),
                ('featured_image', models.ImageField(blank=True, help_text='The proportion of the image should be 388x227', null=True, upload_to='communities')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_details', to='communities.Community')),
            ],
        ),
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='communities', validators=[django.core.validators.validate_image_file_extension, surf.apps.communities.models.validate_featured_size]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='communities', validators=[django.core.validators.validate_image_file_extension, surf.apps.communities.models.validate_logo_size]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='title',
            field=models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='website_url',
            field=models.URLField(blank=True, null=True, validators=[django.core.validators.URLValidator]),
        ),
        migrations.AddConstraint(
            model_name='communitydetail',
            constraint=models.UniqueConstraint(fields=('language_code', 'community'), name='unique languages in community'),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='title',
            field=models.CharField(max_length=80, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='title',
            field=models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
    ]
