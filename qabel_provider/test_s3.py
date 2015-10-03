import requests
import io


def upload(url, payload, key, file):
    data = payload.copy()
    data['key'] = key
    return requests.post(url, files={'file': file}, data=data)


def download(url):
    return requests.get(url)


def check_policy(policy):
    response = upload(policy.base_url, policy.fields, policy.filename('testfile'), io.StringIO('foobar'))
    assert response.status_code == 204, response.text
    get = download(policy.url('testfile'))
    assert get.content == b'foobar'
    assert get.status_code == 200
    return get


def test_sign_policy(s3_session, user):
    policy = s3_session.create_policy(user)
    check_policy(policy)


def test_no_metadata_in_get(s3_session, user):
    policy = s3_session.create_policy(user)
    get = check_policy(policy)
    assert get.headers.get('x-amz-meta-revoke', None) is None


