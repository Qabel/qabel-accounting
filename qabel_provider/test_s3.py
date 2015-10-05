def test_federate_token(s3_session, user, s3_policy):
    token = s3_session.create_token(user, s3_policy.json, 900)
    assert token['Credentials']
    assert token['FederatedUser']
    assert user.username in token['FederatedUser']['FederatedUserId']
    assert token['PackedPolicySize']

