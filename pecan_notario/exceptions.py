from webob.exc import WSGIHTTPException
from webob.response import Response


class JSONValidationException(WSGIHTTPException):
    """
    WebOb doesn't allow setting the explicit content type
    when raising an HTTP exception. It forces the server to use plain text
    or HTML. We require a JSON response because we are validating JSON.

    We subclass form the base HTTP WebOb exception and force the response
    to be JSON.
    """

    code = 400
    title = 'Failed Validation'
    explanation = 'Request failed validation schema'

    def generate_response(self, environ, start_response):
        if self.content_length is not None:
            del self.content_length
        headerlist = list(self.headerlist)
        content_type = 'application/json'
        body = '{"error": "%s"}' % self.detail
        resp = Response(
            body,
            status=self.status,
            headerlist=headerlist,
            content_type=content_type
        )
        resp.content_type = content_type
        return resp(environ, start_response)

