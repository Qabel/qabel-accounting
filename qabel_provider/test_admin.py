from django.core.urlresolvers import reverse


def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200


def test_export_user_data(admin_client, user):
    change_url = reverse('admin:auth_user_changelist')

    primary_email = user.profile.primary_email
    primary_email.verified = True
    primary_email.save()
    response = admin_client.post(change_url, {
        'action': 'export_user_data',
        '_selected_action': [user.pk],
    })
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    assert 'qabel_user,qabeluser@example.com' in response.content.decode()
