from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from project.models import Project
from project.views import PROJECT_LIST_CACHE_KEY


class TestProjectViews(TestCase):

    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_get_projects_list(self):
        """
            Test Get method of ProjectListCreateApiView
        """
        Project.objects.create(name='prj_1', description='test prj_1')
        Project.objects.create(name='prj_2', description='test prj_2')

        response = self.client.get('/api/v1/projects/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'prj_1')

    def test_create_project(self):
        """
            Test Post method of ProjectListCreateApiView
        """
        initial_count = Project.objects.count()

        data = {
            'name': 'New Test Project',
            'description': 'This is a new Test project.',
        }
        response = self.client.post('/api/v1/projects/', data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), initial_count + 1)

    def test_update_project(self):
        """
            Test Put method of ProjectRetrieveUpdateDestroyApiView
        """
        project = Project.objects.create(name='prj_1', description='test prj_1')
        data = {
            'name': 'update_prj_1'
        }
        response = self.client.put(f"/api/v1/projects/{project.id}", data, format='json')
        updated_project = Project.objects.get(id=project.id)

        self.assertEqual(updated_project.name, 'update_prj_1')

    def test_delete_project(self):
        """
            Test Delete method of ProjectRetrieveUpdateDestroyApiView
        """
        project = Project.objects.create(name='prj_1', description='test prj_1')
        response = self.client.delete(f"/api/v1/projects/{project.id}")

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project.id)

    def test_cache_set_correctly(self):
        # Ensure the cache is empty at first
        self.assertIsNone(cache.get(PROJECT_LIST_CACHE_KEY))

        # Create some projects
        prj_1 = Project.objects.create(name='prj_1', description='test prj_1')
        prj_2 = Project.objects.create(name='prj_2', description='test prj_2')

        response = self.client.get('/api/v1/projects/')

        self.assertEqual(response.status_code, 200)
        # After first get request data should be cached :
        cached_data = cache.get(PROJECT_LIST_CACHE_KEY)
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 2)
        # check correct data is cache :
        self.assertEqual(cached_data[0]['name'], prj_1.name)
        self.assertEqual(cached_data[1]['name'], prj_2.name)

    def test_cache_invalidation_on_create_new_project(self):
        # Create some projects
        Project.objects.create(name='prj_1', description='test prj_1')
        Project.objects.create(name='prj_2', description='test prj_2')

        # Get Request to cache result :
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(PROJECT_LIST_CACHE_KEY))

        # Create a new project via POST request
        data = {'name': 'prj_3', 'description': 'test prj_3'}
        response = self.client.post('/api/v1/projects/', data, format='json')

        self.assertEqual(response.status_code, 201)
        # Verify that the cache is invalidated
        self.assertIsNone(cache.get(PROJECT_LIST_CACHE_KEY))

    def test_cache_invalidation_on_put_request(self):
        # Create a project
        prj = Project.objects.create(name='prj_1', description='test prj_1')

        # Get Request to cache result :
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(PROJECT_LIST_CACHE_KEY))

        # Update the project
        data = {'name': 'Updated prj_1', 'description': 'updated project 1'}
        response = self.client.put(f'/api/v1/projects/{prj.id}', data, format='json')

        self.assertEqual(response.status_code, 200)
        # Verify that the cache is invalidated
        self.assertIsNone(cache.get(PROJECT_LIST_CACHE_KEY))

    def test_cache_invalidation_on_delete_request(self):
        # Create a project
        prj = Project.objects.create(name='Project 1', description='Description 1')

        # Get Request to cache result :
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(cache.get(PROJECT_LIST_CACHE_KEY))

        # Delete the project
        response = self.client.delete(f'/api/v1/projects/{prj.id}')
        self.assertEqual(response.status_code, 204)

        # Verify that the cache is invalidated
        self.assertIsNone(cache.get(PROJECT_LIST_CACHE_KEY))
