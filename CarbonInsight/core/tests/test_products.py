from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product
from core.models.company import Company

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):

        #Create User
        self.red_company_user = User.objects.create_user(
            username="1@redcompany.com", email="1@redcompany.com", password="1234567890")

        #Obtain JWT for user
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "1@redcompany.com", "password": "1234567890"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.red_company = Company.objects.create(
            name="Red company BV",
            vat_number="VATRED",
            business_registration_number="NL123456"
        )

        self.blue_company = Company.objects.create(
            name="Blue company BV",
            vat_number="VATBLUE",
            business_registration_number="NL654321"
        )

        CompanyMembership.objects.create(user=self.red_company_user, company=self.red_company)

        self.red_paint = Product.objects.create(
            name="Red paint",
            description="Red paint",
            supplier=self.red_company,
            manufacturer="Red company",
            sku="12345678999",
            is_public=True
        )

        self.red_secret_plans = Product.objects.create(
            name="Secret Plan Red",
            description="Secret Plan Red",
            supplier=self.red_company,
            manufacturer="Red company",
            sku="111222333444",
            is_public=False
        )

        self.blue_paint = Product.objects.create(
            name="Blue paint",
            description="Blue paint",
            supplier=self.blue_company,
            manufacturer="Blue company",
            sku="12345678999",
            is_public=True
        )

        self.blue_secret_plans = Product.objects.create(
            name="Secret Plan Blue",
            description="Secret Plan Blue",
            supplier=self.blue_company,
            manufacturer="Blue company",
            sku="111222333444",
            is_public=False
        )

    def test_products_get_all_products(self):
        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_names = [product["name"] for product in response.data]

        self.assertIn("Red paint", product_names)
        self.assertIn("Secret Plan Red", product_names)
        self.assertNotIn("Blue paint", product_names)
        self.assertNotIn("Secret Plan Blue", product_names)

    def test_products_create_product_own_company(self):
        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_create_product_other_company(self):
        url = reverse("product-list", kwargs={"company_pk": self.blue_company.id})
        response = self.client.post(url,
                                    data={"name": "Orange paint",
                                          "description": "Orange paint",
                                          "manufacturer": "Blue company",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Product.objects.filter(name="Orange paint").exists())

    def test_products_crete_product_missing_name(self):
        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku": "12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_crete_product_missing_manufacturer(self):
        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_crete_product_missing_sku(self):
        url = reverse("product-list", kwargs={"company_pk": self.red_company.id})
        response = self.client.post(url,
                                    data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "is_public": True
                                          })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_retrieve_product_own_public(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertIn("Red paint", product_name)
        self.assertNotIn("Secret Plan Red", product_name)
        self.assertNotIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_own_private(self):
        url = reverse("product-detail", args=[self.red_company.id, 2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertNotIn("Red paint", product_name)
        self.assertIn("Secret Plan Red", product_name)
        self.assertNotIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_other_company_public(self):
        url = reverse("product-detail", args=[self.blue_company.id, 3])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_name = response.data["name"]

        self.assertNotIn("Red paint", product_name)
        self.assertNotIn("Secret Plan Red", product_name)
        self.assertIn("Blue paint", product_name)
        self.assertNotIn("Secret Plan Blue", product_name)

    def test_products_retrieve_product_other_company_private(self):
        url = reverse("product-detail", args=[self.blue_company.id, 4])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_products_update_product_own_company(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_private(self):
        url = reverse("product-detail", args=[self.red_company.id, 2])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_name(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.put(url,
                                   data={"description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_manufacturer(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_missing_sku(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Product.objects.filter(name="Red paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_other_company(self):
        url = reverse("product-detail", args=[self.blue_company.id, 3])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, 4])
        response = self.client.put(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_patch_public(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_own_company_patch_private(self):
        url = reverse("product-detail", args=[self.red_company.id, 2])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())
        self.assertTrue(Product.objects.filter(name="Magenta paint").exists())

    def test_products_update_product_other_company_patch(self):
        url = reverse("product-detail", args=[self.blue_company.id, 3])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, 4])
        response = self.client.patch(url,
                                   data={"name": "Magenta paint",
                                          "description": "Magenta paint",
                                          "manufacturer": "Red company",
                                          "sku":"12345678988",
                                          "is_public": True
                                         }
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())
        self.assertFalse(Product.objects.filter(name="Magenta paint").exists())

    def test_list_products_delete_product_own_company(self):
        url = reverse("product-detail", args=[self.red_company.id, 1])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(name="Red paint").exists())

        url = reverse("product-detail", args=[self.red_company.id, 2])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(name="Secret Plan Red").exists())

    def test_products_delete_product_other_company(self):
        url = reverse("product-detail", args=[self.blue_company.id, 3])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Blue paint").exists())

        url = reverse("product-detail", args=[self.blue_company.id, 4])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(name="Secret Plan Blue").exists())