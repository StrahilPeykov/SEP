from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class RegisterUserProfileAPITests(APITestCase):
    def test_register_user(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "1@company.com",
            "password": "I_Lov3_Carb0nInsight",
            "confirm_password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_register_user_missing_first_name(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "last_name": "Doe",
            "email": "1@company.com",
            "password": "I_Lov3_Carb0nInsight",
            "confirm_password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_missing_last_name(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "email": "1@company.com",
            "password": "I_Lov3_Carb0nInsight",
            "confirm_password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_missing_email(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "last_name": "Doe",
            "password": "I_Lov3_Carb0nInsight",
            "confirm_password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_missing_password(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "1@company.com",
            "confirm_password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_missing_confirm_password(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "1@company.com",
            "password": "I_Lov3_Carb0nInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_missing_unmatching_password_confirm(self):
        url = reverse("register")

        response = self.client.post(url, data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "1@company.com",
            "password": "I_Lov3_Carb0nInsight",
            "confirm_password": "I_Lov3_CarbonInsight"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url2 = reverse("token_obtain_pair")

        login = self.client.post(
            url2, {"username": "1@company.com", "password": "I_Lov3_Carb0nInsight"}, format="json"
        )

        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)