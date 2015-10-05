import boto3


TEST_POLICY = """\
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1444045543000",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::qabel/*"
            ]
        }
    ]
}
"""


class Session:
    def __init__(self):
        self._sts = boto3.client('sts')

    def create_token(self, user, policy, duration):
        return self._sts.get_federation_token(
            Name=user.username,
            Policy=policy,
            DurationSeconds=duration
        )

