from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def setup_shell_completion():
    """Setup shell completion after installation"""
    try:
        from pathlib import Path

        shell = os.environ.get('SHELL', '/bin/bash').split('/')[-1]
        home = Path.home()

        # Create marker so cli.py knows to auto-setup
        tix_dir = home / '.tix'
        tix_dir.mkdir(exist_ok=True)

        print("\n" + "=" * 50)
        print("🚀 TIX Installation Complete!")
        print("=" * 50)
        print("\n✨ Shell completion will be automatically configured on first run.")
        print("   Just run 'tix' and follow any prompts.\n")
        print("📝 To use Tab completion:")
        print("   - Bash/Zsh: source your shell config or start a new terminal")
        print("   - Fish: completion works immediately")
        print("\n" + "=" * 50 + "\n")

    except Exception:
        pass


class PostInstallCommand(install):
    """Post-installation for installation mode"""

    def run(self):
        install.run(self)
        setup_shell_completion()


class PostDevelopCommand(develop):
    """Post-installation for development mode"""

    def run(self):
        develop.run(self)
        setup_shell_completion()


setup(
    name="tix-cli",
    version="0.2.0",
    author="Valentin Todorov",
    author_email="valentin.v.todorov@example.com",
    description="Lightning-fast terminal task manager with auto-completion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheDevOpsBlueprint/tix-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tix=tix.cli:cli",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    keywords="task todo cli terminal productivity manager",
    project_urls={
        "Bug Reports": "https://github.com/TheDevOpsBlueprint/tix-cli/issues",
        "Source": "https://github.com/TheDevOpsBlueprint/tix-cli",
    },
)