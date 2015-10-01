import boto3


class Session:
    def __init__(self, bucket):
        self._bucket = bucket
        self._session = boto3.Session()
        self._s3 = self._session.resource('s3')

    def _conditions(self, user):
        conditions = [
            {"acl": "public-read"},
            ["starts-with", "$key", self.user_prefix(user)]]
        return conditions

    def user_prefix(self, user):
        return "user/{0}/".format(user.id)

    def sign_upload(self, user):
        post = self._s3.meta.client.generate_presigned_post(self._bucket,
                                                            '${filename}',
                                                            Conditions=self._conditions(user),
                                                            Fields={"acl": "public-read"})
        return post['url'], post['fields']
