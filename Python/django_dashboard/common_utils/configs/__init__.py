# package apps.testrail_report.configs
# Handles configuration for importing this package.
 
def _get_package():
    """ Returns the package directory (as pathlib.Path) """
    import os.path
    import pathlib
    _path = os.path.abspath(__file__)
    return pathlib.Path(_path).parent    
 
_package = _get_package()
_ignore = ('__init__', '_TEMPLATE', 'config')
 
# always import 'config' first, because it defines the base classes.
__all__ = ['config'] + [module.stem for module in _package.iterdir() if module.suffix == '.py' and module.stem not in _ignore]


# directly import all modules when this package is imported,
# so that inspect.getmembers(...) can be called on this package
# and be used to access all Project/Config classes.
for module in (module for module in __all__ if module not in globals()):
    try:
        exec('from . import {0}'.format(module), globals())
        
    except ImportError:
        import warnings
        msg = 'Failed to import module {0} from apps.testrail_report.configs'.format(module)
        warnings.warn(msg, ImportWarning)

        