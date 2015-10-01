import requests
import io


def upload(url, payload, key, file):
    data = payload.copy()
    data['key'] = key
    return requests.post(url, files={'file': file}, data=data)


def download(url):
    return requests.get(url)


def test_sign_policy(s3_session, user):
    url, payload = s3_session.sign_upload(user)
    filename = s3_session.user_prefix(user)+'testfile'
    response = upload(url, payload, filename, io.StringIO('foobar'))
    assert response.status_code == 204, response.text
    get = download('/'.join([url, filename]))
    assert get.content == b'foobar'
    assert get.status_code == 200




