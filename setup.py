from setuptools import setup, find_packages

setup(
    name="jofotara_integration",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "lxml>=4.6.3",
        "requests>=2.25.1"
    ],
    entry_points={
        'frappe': [
            'jofotara_integration = jofotara_integration'
        ]
    }
)