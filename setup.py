from pathlib import Path
import setuptools


here = Path(__file__).parent

with open(str(here / 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


with open(str(here / 'requirements.txt'), 'r') as f:
    install_reqs = f.read().strip()
    install_reqs = install_reqs.split("\n")

setuptools.setup(
    name="vs-tabletop",
    author="imr-framework",
    author_email="imr.framework2018@gmail.com",
    description="Virtual Scanner Tabletop Games",
    long_description= long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    url="https://github.com/imr-framework/vs-tabletop",
    version="1.0.0b4", # Beta release
    packages = setuptools.find_packages(),
    install_requires = install_reqs,
    python_requires = '>=3',
    license='License :: OSI Approved :: GNU Affero General Public License v3',
    include_package_data = True,
    entry_points={
        'console_scripts':[
            'vstabletop = vstabletop.app: launch_virtualscanner'
        ]
    }

)