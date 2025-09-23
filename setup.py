from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def setup_message():
    """Display post-installation message"""
    try:
        from pathlib import Path

        shell = os.environ.get('SHELL', '/bin/bash').split('/')[-1]

        print("\n" + "=" * 60)
        print("🚀 TIX Installation Complete!")
        print("=" * 60)
        print("\n✨ Shell completion will be automatically configured on first run.")
        print("   Just run 'tix' and follow any prompts.\n")

        print("📝 Quick Start:")
        print("   tix add 'My first task' -p high  # Add a task")
        print("   tix ls                            # List tasks")
        print("   tix <TAB><TAB>                    # Tab completion")
        print("   t ls                              # Use alias (if configured)")
        print("\n" + "=" * 60)

        print("\n💡 For instant tab completion, run:")
        if 'bash' in shell:
            print("   source ~/.bashrc")
        elif 'zsh' in shell:
            print("   source ~/.zshrc")
        elif 'fish' in shell:
            print("   exec fish")
        else:
            print("   source your shell config file")

        print("\n" + "=" * 60 + "\n")

    except Exception:
        pass


class PostInstallCommand(install):
    """Post-installation for installation mode"""

    def run(self):
        install.run(self)
        setup_message()


class PostDevelopCommand(develop):
    """Post-installation for development mode"""

    def run(self):
        develop.run(self)
        setup_message()


setup(
    name="tix-cli",
    version="0.3.0",
    author="Valentin Todorov",
    author_email="valentin.v.todorov@gmail.com",
    description="Lightning-fast terminal task manager with auto-completion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheDevOpsBlueprint/tix-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        "Topic :: System :: Shells",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
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
    keywords="task todo cli terminal productivity manager shell completion",
    project_urls={
        "Bug Reports": "https://github.com/TheDevOpsBlueprint/tix-cli/issues",
        "Source": "https://github.com/TheDevOpsBlueprint/tix-cli",
        "Documentation": "https://github.com/TheDevOpsBlueprint/tix-cli#readme",
    },
    include_package_data=True,
    zip_safe=False,
)