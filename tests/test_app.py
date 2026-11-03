import unittest
from app_package import create_app, db
from app_package.models import House, Competition, Student, Result

class SchoolPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Seed houses for testing
            default_houses = [
                {"name": "Blue", "emoji": "🔵", "display_color": "text-blue-400", "border_class": "border-blue-500/30", "glow_class": "glow-blue"},
                {"name": "Red", "emoji": "🔴", "display_color": "text-red-400", "border_class": "border-red-500/30", "glow_class": "glow-red"},
                {"name": "Green", "emoji": "🟢", "display_color": "text-emerald-400", "border_class": "border-emerald-500/30", "glow_class": "glow-green"},
                {"name": "Yellow", "emoji": "🟡", "display_color": "text-amber-400", "border_class": "border-amber-500/30", "glow_class": "glow-yellow"}
            ]
            for h in default_houses:
                db.session.add(House(**h))
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_public_index_route(self):
        """Test that the public dashboard loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_protection(self):
        """Test that unauthenticated users cannot access admin dashboard."""
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Teacher Admin Login', response.data)

if __name__ == '__main__':
    unittest.main()