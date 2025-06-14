"""
Tests user's password change API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from core.tests.setup_functions import paint_companies_setup

User = get_user_model()

class ChangePasswordAPITest(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

    def test_change_password_bad_old_password(self):
        """
        Test for an unsuccessful password change where the old provided old password is wrong.
        """
        url = reverse("change_password")

        response = self.client.post(
            url,
            {
                "old_password":"12345699999",
                "new_password":"Ilov3_cab0ninsight",
                "new_password_confirm":"Ilov3_carb0ninsight"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_bad_new_password(self):
        """
        Test for an unsuccessful password change where the new password is not up to safety standards.
        """
        url = reverse("change_password")

        response = self.client.post(
            url,
            {
                "password": "1234567890",
                "new_password": "A",
                "new_password_confirm": "A"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_bad_new_password_confirm(self):
        """
        Test for an unsuccessful password change where the new password confirmation entry does not match the new
         password.
        """

        url = reverse("change_password")

        response = self.client.post(
            url,
            {
                "old_password": "1234567890",
                "new_password": "Ilov3_carb0ninsight",
                "new_password_confirm": "Ilov3_carboninsight"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_good_new_password(self):
        """
        Test for a successful password change.
        """

        url = reverse("change_password")
        url2 = reverse("token_obtain_pair")

        response = self.client.post(
            url,
            {
                "old_password": "1234567890",
                "new_password": "Ilov3_carb0ninsight",
                "new_password_confirm": "Ilov3_carb0ninsight"
            }
        )

        login_old = self.client.post(
            url2, {"username": "1@redcompany.com", "password": "1234567890"}, format="json"
        )

        login_new = self.client.post(
            url2, {"username": "1@redcompany.com", "password": "Ilov3_carb0ninsight"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_old.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(login_new.status_code, status.HTTP_200_OK)