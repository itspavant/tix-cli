from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tix-cli",
    version="0.1.0",
    author="Valentin Todorov",
    author_email="valentin.v.todorov@example.com",
    description="Lightning-fast terminal task manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR-ORG-NAME/tix-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tix=tix.cli:cli",
        ],
    },
)