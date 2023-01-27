
class UpdateProfileDataAPIViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(UpdateProfileAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, UpdateProfileAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(UpdateProfileAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(UpdateProfileAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', UpdateProfileAPIView.__dict__)


class UpdateProfileDataAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('update-profile-api')
        self.data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_status_code_of_201_if_data_profile_is_updated(self):
        response = self.client.put(self.url, self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_it_returns_user_data_after_updated(self):
        response = self.client.put(self.url, self.data)
        self.assertIsNotNone(response.data)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)


class UpdateEmailAPIViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(ChangeEmailAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, ChangeEmailAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(ChangeEmailAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(ChangeEmailAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ChangeEmailAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', ChangeEmailAPIView.__dict__)


class UpdateEmailAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(email='test@test.com')
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('change-email-api')
        self.data = {
            'new_email': "newtest@test.com",
            "password": "secret",
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_422_when_data_is_invalid(self):
        response = self.client.put(self.url, data={})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)

    def test_it_returns_422_if_user_tried_to_enter_the_same_email(self):
        data = {
            'email': "test@test.com",
            "password": "secret",
        }
        response = self.client.put(self.url, data=data)
        self.assertEquals(response.status_code, 422)

    def test_it_change_email_for_user(self):
        self.client.put(self.url, data=self.data)
        self.user.refresh_from_db()
        self.assertEquals(self.user.email, self.data['new_email'])


class UpdatePhoneAPIViewStructure(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(ChangePhoneAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, ChangePhoneAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(ChangePhoneAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(ChangePhoneAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ChangePhoneAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', ChangePhoneAPIView.__dict__)


class UpdatePhoneAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(phone='+201005263977')
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('change-phone-api')
        self.data = {
            'new_phone': "+201005263988",
            "password": "secret",
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_422_when_data_is_invalid(self):
        response = self.client.put(self.url, data={})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)

    def test_it_returns_201_when_user_old_phone_number_is_equal_to_new_number(self):
        data = {
            'new_phone': "+201005263977",
            "password": "secret",
        }
        response = self.client.put(self.url, data=data)
        self.assertEquals(response.status_code, 422)


class ChangePasswordAPIViewStructureAPIView(TestCase):
    def setUp(self):
        self.view = ChangePasswordAPIView

    def test_it_has_serializer_class(self):
        self.assertTrue(hasattr(self.view, 'serializer_class'))

    def test_it_has_model(self):
        self.assertTrue(hasattr(self.view, 'model'))

    def test_it_has_permission_class(self):
        self.assertTrue(hasattr(self.view, 'permission_classes'))

    def test_it_has_update_method(self):
        self.assertIn('update', self.view.__dict__)


class ChangePasswordAPIViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('change_password_api')
        self.data = {
            "new_password1": '12345678Aa',
            "new_password2": '12345678Aa',
            "old_password": 'secret'
        }
        self.password = self.user.password

    def test_it_uses_change_password_serializer(self):
        self.assertIs(ChangePasswordAPIView.serializer_class, ChangePasswordSerializer)

    def test_it_returns_401_when_user_is_unauthenticated(self):
        self.client.logout()
        response = self.client.put(self.url, data={})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_422_invalid_data(self):
        response = self.client.put(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_it_returns_200_on_update(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_it_updates_password(self):
        self.client.put(self.url, data=self.data)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, self.password)
