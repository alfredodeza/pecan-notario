

class TestWrapperValidation(object):

    def setup(self):
        self.app = self.make_app()

    def make_app(self, schema=('key', 'value')):
        import pecan_notario
        from pecan import Pecan, expose, request
        from webtest import TestApp

        simple_schema = schema

        class RootController(object):
            @expose('json')
            @pecan_notario.validate(simple_schema, handler=False)
            def index(self, **kw):
                if request.validation_error is None:
                    return dict(success=True)
                return dict(success=False, error=str(request.validation_error))

        return TestApp(Pecan(RootController()))

    def test_basic_functionality(self):
        body = '{"key":"value"}'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')]
        )
        assert response.json['success'] == True

    def test_basic_error(self):
        body = '{"key":"vvalue"}' # see the extra letter there champ?
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        assert response.json.get('success') == False


    def test_add_the_actual_error(self):
        body = '{"key":"vvalue"}' # see the extra letter there champ?
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        error = response.json.get('error')
        assert error == "-> key -> vvalue did not match 'value'"

    def test_no_errors(self):
        body = '{"key": "value"}'
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        assert response.namespace == {"success": True}


    def test_with_empty_content(self):
        body = ""
        response = self.app.post('/', body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        assert response.json['error'] == "No JSON object could be decoded"
        assert response.json.get('success') == False

    def test_with_invalid_data(self):
        body = '{"foo": [1, 2, 3]}'
        app = self.make_app(schema=('foo', [1,2,3,4]))
        response = app.post('/', body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        error = response.json.get('error')
        assert 'did not match [1, 2, 3, 4]' in error


class TestCustomHandler(TestWrapperValidation):

    def make_app(self, schema=('key', 'value')):
        import pecan_notario
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        simple_schema = schema

        class RootControllerTwo(object):
            @expose('json')
            @pecan_notario.validate(simple_schema, handler='/error')
            def index(self, **kw):
                return dict(success=True)

            @expose('json')
            def error(self, **kw):
                return dict(success=False, error=str(request.validation_error))

        return TestApp(RecursiveMiddleware(Pecan(RootControllerTwo())))


class TestCallableHandler(TestWrapperValidation):

    def make_app(self, schema=('key', 'value')):
        import pecan_notario
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        simple_schema = schema

        class RootControllerTwo(object):
            @expose('json')
            @pecan_notario.validate(
                simple_schema, handler=lambda: '/error'
            )
            def index(self, **kw):
                return dict(success=True)

            @expose('json')
            def error(self, **kw):
                return dict(success=False, error=str(request.validation_error))

        return TestApp(RecursiveMiddleware(Pecan(RootControllerTwo())))


# This is the behavior that gets returned when nothing is configured as
# a handler


class TestDefaultValidation(object):

    def setup(self):
        self.app = self.make_app()

    def make_app(self, schema=('key', 'value')):
        import pecan_notario
        from pecan import Pecan, expose, request
        from webtest import TestApp

        simple_schema = schema

        class RootController(object):
            @expose('json')
            @pecan_notario.validate(simple_schema)
            def index(self, **kw):
                if request.validation_error is None:
                    return dict(success=True)
                return dict(success=False, error=str(request.validation_error))

        return TestApp(Pecan(RootController()))

    def test_basic_functionality(self):
        body = '{"key":"value"}'
        response = self.app.post(
            '/',
            body,
            [('Content-Type', 'application/json')]
        )
        assert response.json['success'] is True

    def test_basic_error(self):
        body = '{"key":"vvalue"}'
        response = self.app.post(
            '/',
            body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        result = response.json.get('error', '')
        assert 'vvalue did not match' in result

    def test_status_int_is_set(self):
        body = '{"key":"vvalue"}'
        response = self.app.post(
            '/',
            body,
            [('Content-Type', 'application/json')],
            expect_errors=True,
        )
        assert response.status_int == 400
