from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    """
    Test case for the index view.
    """

    def test_index_view_status_code(self):
        """
        Test if the index view returns a status code 200.
        """
        response = self.client.get(reverse("fileshare:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_template_used(self):
        """
        Test if the index view uses the correct template.
        """
        response = self.client.get(reverse("fileshare:index"))
        self.assertTemplateUsed(response, "fileshare/index.html")
