from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mobileloadx",
    version="1.0.0",
    author="Matheus Sodré",
    author_email="matheusssoddre98@gmail.com",
    description="Framework de teste de performance para aplicativos mobile (Android/iOS)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eumatheussodre98/mobileloadx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Appium-Python-Client>=2.11.0",
        "selenium>=4.15.0",
        "PyYAML>=6.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "Jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mobileloadx=mobileloadx.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
