from . import aws


def test_federate_token(s3_session, user):
    token = s3_session.create_token(user, aws.TEST_POLICY, 900)
    assert token['Credentials']
    assert token['FederatedUser']
    assert user.username in token['FederatedUser']['FederatedUserId']
    assert token['PackedPolicySize']


