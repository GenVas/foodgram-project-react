from backend.recipes import models
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.recipes import models
from rest_framework.test import APIClient
from backend.users.models import User
from rest_framework.test import RequestsClient


class TestViewSets(APITestCase):
    
    # @classmethod
    # def setUpClass(cls):
    #     pass
    
    def test_endpoints(self):
        user = models.User.objects.create(
            username='first_name',
            last_name='last_name',
            email='email@email.ru',
            password='passwass123321'
        )
        models.Ingredient.objects.create(
            name='testingredient',
            measurement_unit='kilo'
        )

        url = 'api/ingredients/'
        # client = APIClient()
        client = RequestsClient
        
        # client.force_authenticate(user=user)
        response = self.client.get(url=url)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
