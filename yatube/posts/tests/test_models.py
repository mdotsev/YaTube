from django.contrib.auth import get_user_model

from .presets import TestCasePresets

User = get_user_model()


class PostModelTest(TestCasePresets):

    def test_model_post_has_correct_object_names(self):
        """Метод __str__ работает корректно для модели Post."""
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_model_group_has_correct_object_names(self):
        """Метод __str__ работает корректно для модели Group."""
        self.assertEqual(str(self.group), self.group.title)
