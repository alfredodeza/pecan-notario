pecan-notario
-------------
JSON validation for Pecan with Notario (http://notario.cafepais.com).

In its simplest form, you need to define a schema and decorate the
controller method, like::

    schema = ('foo', True)

    @expose()
    @validate(schema)
    def some_controller(self, **kw):
        return dict()


The above controller method, using a Notario schema, will require a ``foo``
key and a ``True`` value otherwise it will (by default) set the HTTP response
to a ``400`` (invalid request) and add the validation error to ``request.pecan['schema'].errors``.


Using a handler
---------------
If more granular control is needed when dealing with an error condition,
a handler can be passed in to the decorator to deal with errors explicitly.

::

    @expose()
    @validate(some_schema, '/some/handler')
    def some_controller(self, **kw):
        return dict()


In this situation '/some/handler' would be a controller method that can deal
directly with the error that was slapped onto the request object (on
``request.validation_error``).

Notario exceptions will include a ``reason`` attribute that will contain the
specific error message that was raised if a custom validator failed with an
error message. In this case, a handler would access this Notario exception
attribute like::

    request.validation_error.reason
