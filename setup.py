from setuptools import setup, find_packages

setup(
    name = "test",
    version = "1.0.0",
    packages = find_packages(),

    description = "egg test demo",
    long_description = "test python setup",
    author = "lhw",
    author_email = "lhw_tyut@163.com",

    license = "GPL",
    keywords = ("test_setup", "egg"),
    platforms = "Independant",
    url = "https://blog.csdn.net/qq_37287621",
    entry_points = {
        'console_scripts': [
            'test_setup = test.helloworld:main'
        ]
    },
    data_files=[
        ('/test/config_file/mysql1.cfg'),
        ('/test/config_file/mysql2.ini'),
    ]
)