import unittest

try:
    import server
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f"Flask preview tests require missing dependency: {exc.name}") from exc


class ServerPreviewTest(unittest.TestCase):
    def test_homepage_renders_task_schedule_and_remaining_tables(self):
        client = server.app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Before tasks", response.data)
        self.assertIn(b"Preview calendar", response.data)
        self.assertIn(b"After tasks", response.data)
        self.assertIn(b"Vacuum", response.data)


if __name__ == "__main__":
    unittest.main()
