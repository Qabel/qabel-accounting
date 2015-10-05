def test_federate_token(s3_session, user, s3_policy):
    actions = s3_policy.policy['Statement'][0]['Action']
    assert 's3:GetObject' in actions
    assert 's3:PutObject' in actions
    assert 's3:ListBucket' in actions
    token = s3_session.create_token(user, s3_policy.json, 900)
    assert token['Credentials']
    assert token['FederatedUser']
    assert user.username in token['FederatedUser']['FederatedUserId']
    assert token['PackedPolicySize']

