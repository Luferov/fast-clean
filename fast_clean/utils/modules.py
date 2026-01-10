import importlib
import os
import sys
from pathlib import Path
from typing import Type, TypeVar

T = TypeVar('T')


def get_modules_by_names(module_name: str, *, include_core_modules: bool = True) -> set[str]:
    """
    Get a list of modules by name.
    """
    cwd = Path(os.getcwd())
    virtual_env_paths = {path.parent for path in cwd.rglob('pyvenv.cfg')}
    module_names: set[str] = set()
    for path in cwd.rglob(f'{module_name}.py'):
        if not any(path.is_relative_to(venv) for venv in virtual_env_paths):
            module_names.add('.'.join(str(path.relative_to(cwd).with_suffix('')).split('/')))
    if include_core_modules:
        module_names.add(f'fast_clean.{module_name}')
        core_cwd = Path(__file__).parent.parent
        for path in (core_cwd / 'contrib').rglob(f'{module_name}.py'):
            module_names.add('.'.join(str(path.relative_to(core_cwd.parent).with_suffix('')).split('/')))
    return module_names


def get_instances(module_names: set[str], instance_type: Type[T]) -> list[T]:
    """
    Get requested objects in the specified modules.
    """
    instances: list[T] = []
    for module_name in module_names:
        module = sys.modules[module_name] if module_name in sys.modules else importlib.import_module(module_name)
        for obj in module.__dict__.values():
            if isinstance(obj, instance_type):
                instances.append(obj)
    return instances
