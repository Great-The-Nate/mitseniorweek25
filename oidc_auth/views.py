import base64
import binascii
import time
import uuid
import urllib
import simplejson as json
import requests
import rsa

from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.contrib.auth import login, get_user_model
from django.db import transaction
from functools import wraps

# Load test libraries
import string
import random
from django.core.urlresolvers import reverse

# Helpers for JWT / JWK handling
def b64url_decode(inp):
    # if someone passed a unicode, convert to ascii bytes
    if isinstance(inp, unicode):
        inp = inp.encode('ascii')
    # pad to multiple of 4
    inp += '=' * (-len(inp) % 4)
    return base64.urlsafe_b64decode(inp)

def get_pubkey_for_kid(jwks_uri, kid):
    """Fetch the providers JWKS and build an rsa.PublicKey for the given kid."""
    jwks = requests.get(jwks_uri, verify=False).json()['keys']
    for jwk in jwks:
        if jwk.get('kid') == kid:
            # decode n and e from base64url into big-endian ints
            n_bytes = b64url_decode(jwk['n'])
            e_bytes = b64url_decode(jwk['e'])
            n = long(binascii.hexlify(n_bytes), 16)
            e = long(binascii.hexlify(e_bytes), 16)
            return rsa.PublicKey(n, e)
    raise ValueError("No matching JWK found for kid %r" % kid)

def verify_jwt(token, jwks_uri, audience, issuer, nonce_expected):
    """
    1) split into header.payload.sig
    2) base64url-decode header+payload -> JSON
    3) fetch the right public key by header['kid']
    4) rsa.verify( header.payload bytes, signature, pubkey )
    5) validate iss, aud, exp, nonce
    6) return payload claims dict
    """
    header_b64, payload_b64, sig_b64 = token.split('.')
    header = json.loads(b64url_decode(header_b64))
    payload = json.loads(b64url_decode(payload_b64))
    sig = b64url_decode(sig_b64)

    # signature verification
    pubkey = get_pubkey_for_kid(jwks_uri, header['kid'])
    message = (header_b64 + '.' + payload_b64).encode('ascii')
    try:
        rsa.verify(message, sig, pubkey)   # defaults to PKCS#1 v1.5 and SHA-256
    except rsa.VerificationError:
        raise ValueError("Invalid JWT signature")

    # claims validation
    now = int(time.time())
    if payload.get('iss') != issuer:
        raise ValueError("Invalid issuer")
    if audience not in payload.get('aud', []):
        raise ValueError("Invalid audience")
    if payload.get('exp', 0) < now:
        raise ValueError("Token has expired")
    if payload.get('nonce') != nonce_expected:
        raise ValueError("Bad nonce")

    return payload

def no_cache(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        resp = view_func(request, *args, **kwargs)
        resp['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp['Pragma']        = 'no-cache'
        resp['Expires']       = '0'
        return resp
    return _wrapped

@no_cache
def oidc_auth(request):
    # generate & stash state+nonce
    state = uuid.uuid4().hex
    nonce = uuid.uuid4().hex
    request.session['oidc_state'] = state
    request.session['oidc_nonce'] = nonce

    params = {
        'response_type': 'code',
        'client_id':     settings.OIDC_CLIENT_ID,
        'redirect_uri':  settings.OIDC_REDIRECT_URI,
        'scope':         settings.OIDC_SCOPE,
        'state':         state,
        'nonce':         nonce,
    }
    auth_url = settings.OIDC_AUTHORIZATION_ENDPOINT + '?' + urllib.urlencode(params)
    return redirect(auth_url)

@no_cache
def oidc_login(request):
    try:
        if 'error' in request.GET:
            raise Exception(request.GET['error'])

        if request.GET.get('state') != request.session.get('oidc_state'):
            raise Exception("Invalid state parameter")

        code = request.GET.get('code')
        if not code:
            raise Exception("Missing authorization code")

        # exchange code -> tokens
        tok = requests.post(
            settings.OIDC_TOKEN_ENDPOINT,
            data={
                'grant_type':   'authorization_code',
                'code':         code,
                'redirect_uri': settings.OIDC_REDIRECT_URI,
            },
            auth=(settings.OIDC_CLIENT_ID, settings.OIDC_CLIENT_SECRET),
            verify=False #TODO: verify correctly
        ).json()

        id_token     = tok.get('id_token')
        access_token = tok.get('access_token')
        if not id_token:
            raise Exception("Missing ID token")

        # verify & decode the ID token
        try:
            claims = verify_jwt(
                id_token,
                settings.OIDC_JWKS_URI,
                audience=settings.OIDC_CLIENT_ID,
                issuer=settings.OIDC_PROVIDER,
                nonce_expected=request.session.get('oidc_nonce')
            )
        except ValueError as e:
            raise Exception(str(e))

        User = get_user_model()
        email = claims.get('sub')
        kerb = email.split('@')[0]
        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                username=kerb,
                defaults={
                    'email': email,
                    'first_name': claims.get('given_name', ''),
                    'last_name': claims.get('family_name', ''),
                }
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
    
        return redirect('home')
    
    except Exception as e:
        context = {"error": str(e)}
        return render(request, 'auth_error.html', context, status=500)


#######################################
# Load test endpoints
#######################################
def oidc_auth_load_test(request):
    time.sleep(0.001)
    return redirect(reverse('oidc_login'))


def oidc_login_load_test(request):
    time.sleep(0.001)

    requests.post(
        'http://google.com',
        data={
            'foo': 'bar',
        },
    )

    time.sleep(0.005)

    res = requests.get('http://google.com')

    User = get_user_model()
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)) + '@example.com'
    kerb = email.split('@')[0]

    try:
        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                username=kerb,
                defaults={
                    'email':      email,
                    'first_name': 'LOAD',
                    'last_name':  'TEST',
                }
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
    except Exception as e:
        # Optionally log or handle DB-related errors more gracefully
        return HttpResponseServerError("User authentication failed, please try again: %s" % e)
    return redirect('home')

