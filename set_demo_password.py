#!/usr/bin/env python
"""One-time script to set demo user password. Delete after use."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='demo')
    user.set_password('DemoArsMP2026!')
    user.save()
    print('SUCCESS: Password updated for demo user')
except User.DoesNotExist:
    # Create user if doesn't exist
    user = User.objects.create_user(
        username='demo',
        email='demo@evaluacion.tfm',
        password='DemoArsMP2026!'
    )
    print('SUCCESS: Demo user created with password')
except Exception as e:
    print(f'ERROR: {e}')
