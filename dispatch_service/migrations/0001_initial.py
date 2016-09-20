from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('redirect_from', models.CharField(help_text='Eg.: <b>buy/qabel-pro-x</b> would make the resulting link <i>https://accounting.qabel.org/dispatch/buy/qabel-pro-x/</i>', max_length=200, primary_key=True, serialize=False)),
                ('to', models.URLField()),
                ('type', models.CharField(choices=[('generic', 'generic link'), ('shareit', 'link to shareit product, cart, ... page')], default='generic', max_length=100)),
            ],
            bases=(models.Model,),
        ),
    ]
