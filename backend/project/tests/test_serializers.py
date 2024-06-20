from django.test import TestCase
from rest_framework.exceptions import ValidationError
from project.serializers import ProjectSerializers


class TestProjectSerializer(TestCase):

    def test_valid_serializer(self):
        valid_data_1 = {
            'name': 'Test Project',
            'description': 'This is a test project.'
        }
        valid_data_2 = {
            'name': 'Test Project 2'
        }

        valid_ser_1 = ProjectSerializers(data=valid_data_1)
        valid_ser_2 = ProjectSerializers(data=valid_data_2)

        self.assertTrue(valid_ser_1.is_valid())
        self.assertTrue(valid_ser_2.is_valid())

    def test_invalid_serializer_missing_name(self):
        invalid_data = {
            'description': 'This is a test project.',
        }
        serializer = ProjectSerializers(data=invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
