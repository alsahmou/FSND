import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


# https://alsahmou.us.auth0.com/authorize?audience=coffee&response_type=token&client_id=qR6a8wUOJcesYoP2KcbBqF3yZ8e2edd2&redirect_uri=https://127.0.0.1:5000/login-results
# live results https://127.0.0.1:8100/login-results#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRySFZvdDM4X2hGeEQ4dzlTQkx0SSJ9.eyJpc3MiOiJodHRwczovL2Fsc2FobW91LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDA5YTI0OTUxODUzYjAwNmEwMGE0MzkiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE2MTEyNDU0OTQsImV4cCI6MTYxMTI1MjY5NCwiYXpwIjoicVI2YTh3VU9KY2VzWW9QMktjYkJxRjN5WjhlMmVkZDIiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.fqvlp6IXqOlgoVsDEgOa0GNiDUYVqcr0sUC62PQJkmoO7lMAWrWjs4U67iCOWEXNtMlJU7ylxBezR1OjPJJ7VH6zfmFqjuPlmPZAizOpqN5IA_3V9lBnSUAf3PWCwaEhoPhxHTo7fQeN6T61z0CNIwL5_0thbB5shzKSONHro9S_fFPKwQhOFBi_bV422CO6ZdnULwbXtOeQwdDZuXt6h2JggqtEsgyRO48p7qfCWUtNuq1totXTFUfSDwhZSC5K6_almorLTtzzL4fp91tnTIUgBBS73mPqpnvufEWj-zM_QnHRR4ipLtWqPVnODY1yvtvIwlJSHAw977ttFGx4eQ&expires_in=7200&token_type=Bearer
# gmail results https://127.0.0.1:8100/login-results#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlRySFZvdDM4X2hGeEQ4dzlTQkx0SSJ9.eyJpc3MiOiJodHRwczovL2Fsc2FobW91LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDA5YTM4YTQ0MWZkNjAwNzA4MWJiZDgiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE2MTEyNDU2NDksImV4cCI6MTYxMTI1Mjg0OSwiYXpwIjoicVI2YTh3VU9KY2VzWW9QMktjYkJxRjN5WjhlMmVkZDIiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.O2TdhkG3BjtGAyWRRqIIePr6LlPvCU2Gp80Cu3j1Gk4ztSHiTVvMv_wkTwvwBWsyo6aka0Olkh-M1pwrVxYb1EaXWUFkP9sGOG-rtUyJAJ5hYsHwv0HQjkBuMMeYQmNYPeMZIgVFbHKXOHffwZafSP4YI4pDPsAoMejp-YNv1ta_8tKW4JloFHuI18Vgg10d0rBGt6qtAqOl_gqdNWd-vglVWhtC3qh2Cwp7DqpOy5Q7j6_lhjzrBS95MJ0bC7yIB07SHwG96tf9oNkNHyplg4eyA0-S6s4xyEtANOjVBXfq0aT3zXoC2mOU25e-_Ngvfx5j194c6QxvJKGqKXrZKw&expires_in=7200&token_type=Bearer
# Barista old token eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik4wTkNOVEEzTWpaQ1FUa3lRMEl6TmtORk0wWXhRVFUwT1RFMFFVVkNSRUpDT1RBME1EUXpOUSJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktZnNuZC5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDY3MTQ4MTQ0MTcwNjk3MTI4OTMiLCJhdWQiOlsiZGV2IiwiaHR0cHM6Ly91ZGFjaXR5LWZzbmQuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTU2MDg5MDE2MCwiZXhwIjoxNTYwODk3MzYwLCJhenAiOiJPSjVwQk9ZSURFa09FVFVmUWo1ajdsSDZFTFcwMkd1MCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiXX0.j9ocW47_exQOkEa10ffh8eijGvrIMxnGRzCmbrXnfaN_8ULsgA7AnWYMtvP8RmPWvT9n8sReWnFuJajUHBUbnBO2GuJ4aM3-WDUBeJT0X_mpGUWs4lxaNTbIkWdiWPTsEiRnP3wT-dU_v3Olw2PB4UMajMIjSH-IdF2Y1CiJIOaM0gV44RGZRyRvj6C2_mOkMfoXxzw-HrVvTRCo1NcUPea5Bs04POni7azx-B7FstP_HLm0dEbbge4XbmovHwlIXknIoI8PbuGXeLBqE2hv8fErKFBuIykxzK0nErH5zSPCrkM-_9smb8TLGAH-E5j1KQb6SHDKtcV_QHnsUYFuXA
# Manager old token eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik4wTkNOVEEzTWpaQ1FUa3lRMEl6TmtORk0wWXhRVFUwT1RFMFFVVkNSRUpDT1RBME1EUXpOUSJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktZnNuZC5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDY3MTQ4MTQ0MTcwNjk3MTI4OTMiLCJhdWQiOlsiZGV2IiwiaHR0cHM6Ly91ZGFjaXR5LWZzbmQuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTU2MDg4OTU5NiwiZXhwIjoxNTYwODk2Nzk2LCJhenAiOiJPSjVwQk9ZSURFa09FVFVmUWo1ajdsSDZFTFcwMkd1MCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcyIsImdldDpkcmlua3MtZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.Qk-5FC2X_RUkK00WKARYCKw_877XFuaT5ND3f3ObD9Ly1e1GMfJXhi3McV12binGGCw6x241erIjGB0t8WbWdU3bYpIVD1klZ64DVLQ8Q2LQ2NzB3eFEOgGLL85az1jIDbRiuATIRbbBOWILPJ6h6KR9L5hExklf2zuj3Bnwm7zMRmVpIJmjrUt4bWjtTOguOwJ0IVQsk4PDjGxzwfrUWFCFNDqN_u15JNLxeH21C-QvCpHs3D4Aodeh1qFUuWHfK_Gyfu91AitXPTVZRX9eZbUOVkGT3JMn4sKn9oGaKFTx2E-Y4DmoECG0uWImbX_wiRjx4aTeo7Q7hKSReMToPA

AUTH0_DOMAIN = 'alsahmou.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    '''
        it should attempt to get the header from the request
            it should raise an AuthError if no header is present
        it should attempt to split bearer and the token
            it should raise an AuthError if the header is malformed
        return the token part of the header
    '''
    auth = request.headers.get('Authorization', None)

    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401) 

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token


def check_permissions(permission, payload):
    '''
        @INPUTS
            permission: string permission (i.e. 'post:drink')
            payload: decoded jwt payload

        it should raise an AuthError if permissions are not included in the payload
        it should raise an AuthError if the requested permission string is not in the payload permissions array
        return true otherwise
    '''
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not found.'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Unauthorized user.'
    }, 403)
    return True


def verify_decode_jwt(token):
    '''
        @INPUTS
            token: a json web token (string)

        it should be an Auth0 token with key id (kid)
        it should verify the token using Auth0 /.well-known/jwks.json
        it should decode the payload from the token
        it should validate the claims
        return the decoded payload
    '''
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    '''
        @INPUTS
            permission: string permission (i.e. 'post:drink')

        it should use the get_token_auth_header method to get the token
        it should use the verify_decode_jwt method to decode the jwt
        it should use the check_permissions method validate claims and check the requested permission
        return the decorator which passes the decoded payload to the decorated method
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except AuthError as e:
                abort(e.status_code)
            try:
                check_permissions(permission, payload)
            except AuthError as e:
                abort(e.status_code)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator