from unittest import TestCase


class TestWrapperValidation(TestCase):

    def setUp(self):
        import pecan_notario
        from pecan import Pecan, expose, request
        from webtest import TestApp

        simple_schema = ('key', 'value')
        #simple_schema = {
        #    "type": "array",
        #    "items": [
        #        {"type": "string"},
        #        {"type": "object",
        #            "properties": {
        #                "bar":{
        #                    "items": [
        #                        {"type": "string"},
        #                        {"type": "any"},
        #                        {"type": "number"},
        #                        {"type": "integer"}
        #                    ]
        #                }
        #            }
        #        }
        #    ]
        #}

        class RootController(object):
            @expose('json')
            @pecan_notario.with_schema(simple_schema)
            def index(self, **kw):
                if request.validation_error is None:
                    return dict(success=True)
                return dict(success=False, error=str(request.validation_error))

        self.app = TestApp(Pecan(RootController()))

    def test_basic_functionality(self):
        body = '{"key":"value"}'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.body == '{"success": true}'
        assert response.namespace == {"success": True}
        #assert response.validation_error is None

    def test_basic_error(self):
        body = '{"key":"vvalue"}'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.body == '{"success": true}'
        assert response.namespace == {"success": True}
        #assert response.request.validation_error is None

    def test_no_errors(self):
        body = '["foo", {"bar":["baz", null, 1.0, 2]}]'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.body == '{"success": true}'
        assert response.namespace == {"success": True}
        #assert response.request.validation_error is None

    def test_with_empty_content(self):
        body = ''
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.body == '{"success": false, "error": "No JSON object could be decoded"}'  # noqa
        assert response.namespace == {"success": False, "error": "No JSON object could be decoded"}  # noqa
        #assert response.request.validation_error is not None

    def test_with_invalid_data(self):
        body = '[1, 2, 3]'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.body == '{"success": false, "error": "Length of list [1, 2, 3] for field \'_data\' is not equal to length of schema list"}'  # noqa
        assert response.namespace == {"success": False, "error": "Length of list [1, 2, 3] for field \'_data\' is not equal to length of schema list"}  # noqa
        #assert response.request.validation_error is not None


class TestCustomHandler(TestWrapperValidation):
    def setUp(self):
        import pecan_notario
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        simple_schema = {
            "type": "array",
            "items": [
                {"type": "string"},
                {"type": "object",
                    "properties": {
                        "bar":{
                            "items": [
                                {"type": "string"},
                                {"type": "any"},
                                {"type": "number"},
                                {"type": "integer"}
                            ]
                        }
                    }
                }
            ]
        }

        class RootControllerTwo(object):
            @expose('json')
            @pecan_notario.with_schema(simple_schema, handler='/error')
            def index(self, **kw):
                return dict(success=True)

            @expose('json')
            def error(self, **kw):
                return dict(success=False, error=str(request.validation_error))

        self.app = TestApp(RecursiveMiddleware(Pecan(RootControllerTwo())))


class TestCallableHandler(TestWrapperValidation):

    def setUp(self):
        import pecan_notario
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        simple_schema = {
            "type": "array",
            "items": [
                {"type": "string"},
                {"type": "object",
                    "properties": {
                        "bar":{
                            "items": [
                                {"type": "string"},
                                {"type": "any"},
                                {"type": "number"},
                                {"type": "integer"}
                            ]
                        }
                    }
                }
            ]
        }

        class RootControllerTwo(object):
            @expose('json')
            @pecan_notario.with_schema(
                simple_schema, handler=lambda: '/error'
            )
            def index(self, **kw):
                return dict(success=True)

            @expose('json')
            def error(self, **kw):
                return dict(success=False, error=str(request.validation_error))

        self.app = TestApp(RecursiveMiddleware(Pecan(RootControllerTwo())))
