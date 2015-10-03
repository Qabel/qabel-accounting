import boto3
import uuid


class SignedPolicy:
    def __init__(self, session, user):
        self.session = session
        self.user = user
        self.base_url, self.fields = session.sign_upload(user)
        self.prefix = session.user_prefix(user)
        self.fields['x-amz-meta-revoke'] = uuid.uuid4().urn

    def filename(self, basename):
        return self.prefix + basename

    def url(self, basename):
        return self.base_url + '/' + self.filename(basename)


class Session:
    def __init__(self, bucket):
        self._bucket = bucket
        self._session = boto3.Session()
        self._s3 = self._session.resource('s3')

    def create_policy(self, user):
        return SignedPolicy(self, user)

    def _conditions(self, user):
        conditions = [
            {"acl": "public-read"},
            ["starts-with", "$x-amz-meta-revoke", ''],
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
