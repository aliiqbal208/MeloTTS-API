"""
MeloTTS-API Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-e"):
                # Remove version constraints for setup.py
                if "==" in line:
                    requirements.append(line.split("==")[0])
                elif ">=" in line:
                    requirements.append(line.split(">=")[0])
                else:
                    requirements.append(line)
        return requirements

setup(
    name="melotts-api",
    version="1.0.0",
    author="MeloTTS-API Team",
    author_email="team@melotts-api.dev",
    description="High-performance Text-to-Speech API service powered by MeloTTS",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MeloTTS-API",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/MeloTTS-API/issues",
        "Source": "https://github.com/yourusername/MeloTTS-API",
        "Documentation": "https://github.com/yourusername/MeloTTS-API#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "pre-commit>=3.0.0",
            "jupyter>=1.0.0",
            "ipython>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "melotts-api=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    keywords=[
        "text-to-speech",
        "tts",
        "api",
        "fastapi",
        "melotts",
        "docker",
        "multilingual",
        "speech-synthesis",
        "rest-api",
        "python",
    ],
    zip_safe=False,
)
