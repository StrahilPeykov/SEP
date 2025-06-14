"""
Tests for the user API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class UserProfileAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

    def test_delete_current_user_authenticated(self):
        """
        Test case to delete the currently active user.
        """

        url = reverse("user_profile")

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.red_company_user1.id).exists())
        #Assert that other users were not deleted
        self.assertTrue(User.objects.filter(id=self.red_company_user2.id).exists())

    def test_delete_current_user_unauthorized(self):
        """
        Test for trying to delete currently active user when there is no active user.
        """

        self.client.credentials()
        url = reverse("user_profile")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(id=self.red_company_user1.id).exists())

    def test_switch_user_and_delete_current_user_authenticated_authorized(self):
        """
        Test for changing accounts and then deleting the newly logged in user.
        """

        self.user3 = User.objects.create_user(username="3@company.com", email="3@company.com",
                                              password="1234567890")
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "3@company.com", "password": "1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        url = reverse("user_profile")

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user3.id).exists())
        # Assert that other users were not deleted
        self.assertTrue(User.objects.filter(id=self.red_company_user2.id).exists())
        self.assertTrue(User.objects.filter(id=self.red_company_user1.id).exists())
        
    def test_delete_current_user_and_check_company_membership(self):
        """
        Test for deleting the currently active user and checking if the user is still authorized to manage the company.
        """

        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.red_company_user1,
                company=self.red_company
            ).exists()
        )

        url = reverse("user_profile")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.red_company_user1,
                company=self.red_company
            ).exists()
        )
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.red_company_user2,
                company=self.red_company
            ).exists()
        )

    def test_update_personal_user_details_put_authenticated_authorized(self):
        """
        Test for updating personal information of the currently active user with a put request.
        """

        self.assertFalse(
            User.objects.filter(
                username="1@redcompany.com",
                first_name="John",
                last_name="Pork"
            ).exists())

        url = reverse("user_profile")

        response = self.client.put(url, {"username": "1@redcompany.com", "email": "1@redcompany.com",
                                         "first_name": "John", "last_name": "Pork"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            User.objects.filter(
                username="1@redcompany.com",
                first_name="John",
                last_name="Pork"
            ).exists())

    def test_update_personal_user_details_put_missing_username_authenticated_authorized(self):
        """
        Test for updating personal information of the currently active user with a missing username using a put request.
        """

        url = reverse("user_profile")

        response = self.client.put(url, {"email": "test@testmissing.com",
                                         "first_name": "James", "last_name": "Lasagne"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_personal_user_details_patch_authenticated_authorized(self):
        """
        Test for updating personal information of the currently active user with a patch request.
        """

        url = reverse("user_profile")

        response = self.client.patch(url, {"username": "1@redcompany.com", "email": "1@redcompany.com",
                                         "first_name": "John2", "last_name": "Pork2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            User.objects.filter(
                username="1@redcompany.com",
                first_name="John2",
                last_name="Pork2"
            ).exists())

    def test_update_personal_user_details_unauthorized(self):
        """
        Test for trying to update personal information of the currently active user without having an active user.
        """

        self.client.credentials()
        url = reverse("user_profile")

        response = self.client.put(url, {"username": "1@redcompany.com", "email": "1@redcompany.com",
                                         "first_name": "John2", "last_name": "Pork2"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_personal_user_details_put_to_existing_username(self):
        """
        Test for trying to update username of the currently active user with an existing username with a put request.
        """

        url = reverse("user_profile")

        response = self.client.put(url, {"username": "2@redcompany.com", "email": "2@redcompany.com",
                                         "first_name": "John", "last_name": "Pork"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_personal_user_details_patch_to_existing_username(self):
        """
        Test for trying to update username of the currently active user with an existing username with a patch request.
        """

        url = reverse("user_profile")

        response = self.client.patch(url, {"username": "2@redcompany.com",
                                         "first_name": "John", "last_name": "Pork"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_personal_user_details_put_different_username_and_email(self):
        """
        Test updating personal information of the currently active user with unmatching username and email with a put
         request.
        """

        url = reverse("user_profile")

        response = self.client.put(url, {"username": "3@newcompany.com", "email": "5@oldcompany.com",
                                           "first_name": "John", "last_name": "Pork"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        # Username should be the same as email, as it is internally enforced
        self.assertEqual(get_response.data["username"], "5@oldcompany.com")
        self.assertEqual(get_response.data["username"], "5@oldcompany.com")
        self.assertEqual(get_response.data["first_name"], "John")
        self.assertEqual(get_response.data["last_name"], "Pork")

    def test_update_personal_user_details_patch_different_username_and_email(self):
        """
        Test updating personal information of the currently active user with unmatching username and email with a patch
         request.
        """

        url = reverse("user_profile")

        response = self.client.patch(url, {"username": "3@newcompany.com", "email": "5@oldcompany.com",
                                           "first_name": "John", "last_name": "Pork"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        # Username should be the same as email, as it is internally enforced
        self.assertEqual(get_response.data["username"], "5@oldcompany.com")
        self.assertEqual(get_response.data["username"], "5@oldcompany.com")
        self.assertEqual(get_response.data["first_name"], "John")
        self.assertEqual(get_response.data["last_name"], "Pork")