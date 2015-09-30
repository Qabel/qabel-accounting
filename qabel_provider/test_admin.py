
def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200


def test_inline_user_profile(admin_client):
    response = admin_client.get('/admin/auth/user/1/')
    assert b'Storage quota:' in response.content
