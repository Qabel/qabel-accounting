import boto3


class Session:
    def __init__(self):
        self._sts = boto3.client('sts')

    def _conditions(self, user):
        conditions = [
            {"acl": "public-read"},
            ["starts-with", "$x-amz-meta-revoke", ''],
            ["starts-with", "$key", self.user_prefix(user)]]
        return conditions

    def user_prefix(self, user):
        return "user/{0}/".format(user.id)

    def create_token(self, user, policy, duration):
        return self._sts.get_federation_token(
            Name=user.username,
            Policy=policy,
            DurationSeconds=duration
        )

