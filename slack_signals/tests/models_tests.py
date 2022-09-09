from django.test import TestCase
from django.core.exceptions import ValidationError

from slack_signals.models import Todo


class TodoTestCase(TestCase):
    def test_create(self):
        before_count = Todo.objects.count()
        Todo.objects.create(text="text_value")
        after_count = Todo.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def test_required_field(self):
        todo = Todo()
        with self.assertRaises(ValidationError) as e:
            todo.full_clean()
            self.assertIn('This field cannot be blank.', e.message_dict)

    def test_str(self):
        todo = Todo(text="text_value")
        self.assertEqual(str(todo), "text_value")
