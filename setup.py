from setuptools import setup, find_packages

setup(
    name="jo_fotara",
    version="1.0.0",
    description="ERPNext JoFotara (Jordan E-Invoicing) Integration",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "frappe>=15.0.0",
        "lxml",
        "requests"
    ],
    zip_safe=False,
)