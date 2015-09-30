def test_login(api_client, user):
    response = api_client.post('/api-auth/login', {'username': user.username, 'password': 'password'})
    # redirect to profile page which we can ignore.
    assert response.status_code == 301
