from setuptools import setup, find_packages
setup(
    name = "daycare_ethics",
    version = "0.2.3",
    packages = find_packages(),
    package_data = {
        'daycare_ethics': [
            'www/css/*',
            'www/img/*',
            'www/js/*',
            'www/*.png',
            'www/*.pdf',
            'www/*.html',
        ],
    }
)