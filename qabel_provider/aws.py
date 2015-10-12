import json
import boto3


class Policy:

    def __init__(self, user):
        self.user = user
        self.policy = {
            "Version": "2012-10-17",
            "Statement": []
        }
        self.append(
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                ],
                "Resource": [
                    "arn:aws:s3:::{}/{}".format(self.user.profile.bucket,
                                                self.user.profile.prefix)
                ]
            })

    def append(self, statement):
        self.policy['Statement'].append(statement)

    @property
    def json(self):
        return json.dumps(self.policy)


class Session:
    def __init__(self):
        self._sts = boto3.client('sts')

    def create_token(self, user, policy, duration):
        return self._sts.get_federation_token(
            Name=user.username,
            Policy=policy,
            DurationSeconds=duration
        )

