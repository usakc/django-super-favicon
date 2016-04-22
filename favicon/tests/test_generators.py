import re
from django.test import TestCase
from PIL import Image
from favicon.tests.utils import HANDLED_FILES, BASE_IMG, EXPECTED_FILES,\
    FakeStorage
from favicon.generators import generate, PNG_SIZES, WINDOWS_PNG_SIZES

SRC_REG = re.compile(r'src="/static/([^"]*)"')


class GenerateTest(TestCase):
    def setUp(self):
        self.storage = FakeStorage()

    def tearDown(self):
        HANDLED_FILES.clean()

    def test_generate(self):
        generate(BASE_IMG, self.storage)
        for name, content in HANDLED_FILES['written_files'].items():
            self.assertIn(name, EXPECTED_FILES)
            self.assertTrue(content.size)
        # Test ICO file
        ico = self.storage._open('favicon.ico')
        self.assertEqual(Image.open(ico).format, 'ICO')
        # Test PNG
        for size in PNG_SIZES:
            name = 'favicon-%d.png' % size
            self.assertTrue(self.storage.exists(name))
            png = self.storage._open(name)
            img = Image.open(png)
            self.assertEqual(img.format, 'PNG')
            self.assertEqual(img.size, (size, size))
        # Test Windows PNG
        for size, name in WINDOWS_PNG_SIZES:
            self.assertTrue(self.storage.exists(name))
            png = self.storage._open(name)
            img = Image.open(png)
            self.assertEqual(img.format, 'PNG')
            if size[0] != size[1] or size[0] > 440:
                continue
            self.assertEqual(img.size, size)
        # Test ieconfig.xml
        ieconfig = self.storage._open('ieconfig.xml').read()
        for name in SRC_REG.findall(ieconfig):
            self.assertTrue(self.storage.exists(name))