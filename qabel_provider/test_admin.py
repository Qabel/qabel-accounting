from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.urls import reverse


def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200


def test_export_user_data(admin_client, user):
    change_url = reverse('admin:auth_user_changelist')

    primary_email = user.profile.primary_email
    primary_email.verified = True
    primary_email.save()

    # No email address
    no_mail = User.objects.create_user('no_mail', 'no_mail@example.com', 'password')

    # No confirmed email address
    unconfirmed = User.objects.create_user('unconfirmed', 'unconfirmed@example.com', 'password')
    EmailAddress.objects.create(user=unconfirmed, email=unconfirmed.email, primary=True)

    # Unrelated user
    User.objects.create_user('unrelated', 'unrelated@example.com', 'password')

    response = admin_client.post(change_url, {
        'action': 'export_user_data',
        '_selected_action': [user.pk, no_mail.pk, unconfirmed.pk],
    })
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    content = response.content.decode()
    assert 'qabel_user,qabeluser@example.com' in content
    assert 'no_mail' not in content
    assert 'unconfirmed' not in content
    assert 'unrelated' not in content
