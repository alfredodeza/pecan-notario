from pecan import request, redirect

import json
import notario
from notario.exceptions import Invalid
from pecan_notario.exceptions import JSONValidationException

__all__ = ['validate']


def validate(schema, handler=None, status=400, **kw):
    """
    Used to decorate a Pecan controller with form creation for GET | HEAD and
    form validation for anything else (e.g., POST | PUT | DELETE ).

    For an HTTP POST or PUT (RFC2616 unsafe methods) request, the schema is
    used to validate the request body. Errors from validation (if any) are
    accessible at ``request.pecan['schema'].errors``.

    Optionally, validation errors can be made to trigger an internal HTTP
    redirect by specifying a ``handler`` in the ``error_cfg`` argument.

    :param schema: A JSON schema.
    :param handler: A URI path to redirect to when schema validation fails.
                    Can also be a callable that returns a URI path.
    :param status: The HTTP response code to use. Defaults to 400
    """
    def deco(f):

        def wrapped(*args, **kwargs):
            request.validation_error = None

            if request.method in ('POST', 'PUT'):
                try:
                    body = request.body.decode()
                    if not body:
                        raise ValueError('No JSON object could be decoded')
                    data = json.loads(body)
                    notario.validate(data, schema)
                except (Invalid, ValueError) as error:
                    # TODO: It would be nice if we could have a sane default
                    # here where we set the response body instead of requiring
                    # a handler
                    request.validation_error = error
                    if handler:
                        redirect_to_handler(error, handler)
                    # a controller can say `handler=False` to signal they don't
                    # want to delegate, not even to the fallback
                    if handler is None:
                        headers = {'Content-Type': 'application/json'}
                        raise JSONValidationException(
                            detail=error,
                            headers=headers
                        )

            return f(*args, **kwargs)

        return wrapped

    return deco


def redirect_to_handler(error, location):
    """
    Cause a requset with an error to internally redirect to a URI path.

    This is generally for internal use, but can be called from within a Pecan
    controller to trigger a validation failure from *within* the controller
    itself, e.g.::

        @expose()
        @validate(some_schema, '/some/handler')
        def some_controller(self, **kw):
            if some_bad_condition():
                error_exception = ...
                redirect_to_handler(error_exception, '/some/handler')
    """
    if callable(location):
        location = location()
    request.environ['REQUEST_METHOD'] = 'GET'
    redirect(location, internal=True)
