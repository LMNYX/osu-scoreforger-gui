from distutils.core import setup
import py2exe

# build into one exe file
setup(
    console=[
        {
            'script': 'run.py',
            'dest_base': 'ScoreForger'
        }
    ],
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
        }
    },
    zipfile=None,
)