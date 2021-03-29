from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'Console'

executables = [
    Executable('redcli.py', base=base)
]

setup(name='REDClient',
      version = '1.0',
      author = 'Jerald Thomas',
      description = 'A python client and cli application for the Remote Experiment Datalogging framework.',
      py_modules = ['redclient'],
      setup_requires = ['cs-freeze'],
      options = {'build_exe': build_options},
      executables = executables)
