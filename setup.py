from setuptools import setup

setup(
    name="booker",
    author="tanakenology",
    author_email="tanakenology@gmail.com",
    url="https://github.com/tanakenology/booker",
    packages=["booker"],
    license="tanakenology",
    install_requires=[
        "selenium==4.1.3",
        "webdriver-manager==3.5.4",
        "python-dotenv==0.20.0",
        "boto3==1.22.9",
        "jsonlines==3.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "pylint",
            "autopep8",
            "pytest",
            "pytest-randomly",
        ]
    },
    entry_points={"console_scripts": [("booker=booker:main")]},
)
