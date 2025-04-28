import base64
import binascii
import time
import uuid
import urllib
import simplejson as json
import requests
import rsa

from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import login, get_user_model

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

def oidc_login(request):
    if 'error' in request.GET:
        return HttpResponseBadRequest("OIDC error: %s" % request.GET['error'])

    if request.GET.get('state') != request.session.get('oidc_state'):
        return HttpResponseBadRequest("Invalid state parameter")

    code = request.GET.get('code')
    if not code:
        return HttpResponseBadRequest("Missing authorization code")

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
        return HttpResponseBadRequest("No ID token returned")

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
        return HttpResponseBadRequest("JWT validation failed: %s" % e)

    # Get + store user info
    ui = requests.get(
        settings.OIDC_USERINFO_ENDPOINT,
        headers={'Authorization': 'Bearer %s' % access_token},
        verify=False
    ).json()

    User = get_user_model()
    email = ui.get('email') or claims.get('email')
    kerb = email.split('@')[0]
    user, _ = User.objects.get_or_create(
        username=kerb,
        defaults={
            'email':      email,
            'first_name': ui.get('given_name', claims.get('given_name', '')),
            'last_name':  ui.get('family_name', claims.get('family_name', '')),
        }
    )
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return redirect('home')
