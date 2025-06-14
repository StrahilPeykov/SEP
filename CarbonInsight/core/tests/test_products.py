"""
Tests for product API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product
from core.models.company import Company
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        paint_companies_setup(self)
        self.magenta_paint.delete()
        self.purple_paint.delete()

    def test_products_get_all_products(self):
        """
        Test for getting the list of all products that the company owns.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_names = [product["name"] for product in response.data]

        self.assertIn("Red paint", product_names)
        self.assertIn("Secret Plan Red", product_names)
        self.assertNotIn("Blue paint", product_names)
        self.assertNotIn("Secret Plan Blue", product_names)

    def test_products_create_product_own_company(self):
        """
        Test for creating a product under a company that the user that the user is authorized to manage.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_create_product_other_company(self):
        """
        Test for creating a product under a company that the user that the user is not authorized to manage.
        """

        url = reverse("product-list", kwargs={"company_pk": self.blue_company.id})
        response = self.client.post(url,
                                    data={"name": "Orange paint",
                                          "description": "Orange paint",
                                          "manufacturer_name": "Blue company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Product.objects.filter(name="Orange paint").exists())

    def test_products_create_product_missing_name(self):
        """
        Test for trying to create a product without name.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku": "12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_create_product_missing_manufacturer(self):
        """
        Test for trying to create a product without manufacturer.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_create_product_missing_sku(self):
        """
        Test for trying to create a product without sku.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_retrieve_product_own_public(self):
        """
        Test for getting the information for a specific public product that the company owns.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertIn("Red paint", product_name)
        self.assertNotIn("Secret Plan Red", product_name)
        self.assertNotIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_own_private(self):
        """
        Test for getting the information for a specific private product that the company owns.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_secret_plans.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertNotIn("Red paint", product_name)
        self.assertIn("Secret Plan Red", product_name)
        self.assertNotIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_other_company_public(self):
        """
        Test for getting the information for a specific public product that another company owns.
        """

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertNotIn("Red paint", product_name)
        self.assertNotIn("Secret Plan Red", product_name)
        self.assertIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_other_company_private(self):
        """
        Test for getting the information for a specific private product that another company owns.
        """
        url = reverse("product-detail", args=[self.blue_company.id, self.blue_secret_plans.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_products_update_product_own_company(self):
        """
        Test for updating the information for a specific public product that the company owns with a put request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_private(self):
        """
        Test for updating the information for a specific private product that the company owns with a put request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_secret_plans.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_name(self):
        """
        Test for updating the information of a product owned by the company with a missing name with a put request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.put(url,
                                   data={"description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_manufacturer(self):
        """
        Test for updating the information of a product owned by the company with a missing manufacturer with a put
         request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_sku(self):
        """
        Test for updating the information of a product owned by the company with a missing sku with a put request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_other_company(self):
        """
        Tests for updating the information for a specific products that another company owns with put requests.
        """

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_secret_plans.id])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_patch_public(self):
        """
        Test for updating the information of a public product owned by the company with a patch request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_patch_private(self):
        """
        Test for updating the information of a private product owned by the company with a patch request.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_secret_plans.id])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_other_company_patch(self):
        """
        Tests for updating the information of specific products that another company owns with a patch requests.
        """

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_secret_plans.id])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_list_products_delete_product_own_company(self):
        """
        Test for deleting a product owned by the company.
        """

        url = reverse("product-detail", args=[self.red_company.id, self.red_paint.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())

        url = reverse("product-detail", args=[self.red_company.id, self.red_secret_plans.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())

    def test_products_delete_product_other_company(self):
        """
        Test for deleting a product owned by another company.
        """

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_paint.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, self.blue_secret_plans.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Secret Plan Blue").exists())

    def test_products_create_product_own_company_duplicate_product(self):
        """
        Test for trying to create duplicate product.
        """

        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})

        response = self.client.post(url,
                                    data={"name": "Red paint",
                                          "description": "Red paint",
                                          "manufacturer_name": "Red company",
                                          "manufacturer_country": "NL",
                                            "manufacturer_city": "Eindhoven",
                                            "manufacturer_street": "De Zaale",
                                            "manufacturer_zip_code": "5612AZ",
                                            "year_of_construction": 2025,
                                            "family": "Paint",
                                          "sku":"12345678999",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.filter(name="Red paint").count(), 1)