`/mit/__init__.py` contains some useful functionality for Django applications
running at MIT, particularly on the scripts.mit.edu platform

- `zephyr(msg, clas, instance, rcpt)` sends a zephyr (by shelling out to
  zwrite).  This may be useful for debugging or logging
- `ScriptsRemoteUserMiddleware` and `ScriptsRemoteUserBackend` work together to
  auto-create users from certificates on scripts.mit.edu-hosted sites. Account
  details are automatically retrieved from LDAP.
- `scripts_login` is a view that tries to log users into a site using certs.

To use them, you'll probably want to symlink or copy the `mit` directory into
your project, add it to your apps list, and modify your middlewares and auth
backend appropriately. Do *not* link this (the `django` directory) into your
app; it's reasonably likely to break your `import django.foo` statements.

This code is descended from work on
[Remit](https://remit.scripts.mit.edu/trac/) and the [ASA
DB](https://asa.scripts.mit.edu/trac/); current and past bugs are likely to be
filed there.

Using certificate authentication
--------------------------------

1. Copy the `mit` directory into your project
2. Update settings.py
   - Add `mit.ScriptsRemoteUserMiddleware` to the end of `MIDDLEWARE_CLASSES`
   - Add `mit.ScriptsRemoteUserBackend` to the beginning of
     `AUTHENTICATION_BACKENDS`
3. Add `url(r'^accounts/login/',  'mit.scripts_login',  name='login', )` to
   your `urls.py`. This causes `@login_required` and similar mechanisms to
   automatically redirect users to port 444 and log them in with certificates.
