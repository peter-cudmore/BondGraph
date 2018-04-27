"""
Bond Graph Model base files.
"""

import logging
import copy

from .component_manager import get_component, base_id

logger = logging.getLogger(__name__)


def new(component, name=None, library=base_id, value=None):
    """
    Creates a new Bond Graph from a library component.

    Args:
        component(str or obj): The type of component to create.
         If a string is specified, the the component will be created from the
         appropriate libaray. If an existing bond graph is given, the bond
         graph will be cloned.
        name (str): The name for the new component
        library (str): The library from which to find this component (if
        component is specified by string).
        value:

    Returns: instance of :obj:`BondGraph`

    """
    if isinstance(component, str):
        build_args = get_component(component, library)

        if name:
            build_args.update({"name": name})
        if value:
            _update_build_params(build_args, value)

        cls =_find_subclass(
            build_args["class"], BondGraphBase
        )
        del build_args["class"]

        return cls(type=component, **build_args)

    elif isinstance(component, BondGraphBase):
        obj = copy.copy(component)
        if name:
            obj.name = name
        if value:
            _update_build_params(obj.__dict__, value)

        return obj

    else:
        raise NotImplementedError(
            "New not implemented for object {}", component
        )


def _update_build_params(build_args, value):
    if isinstance(value, (list, tuple)):
        assignments = zip(value, build_args["params"].keys())
        for param, v in assignments:
            build_args["params"][param] = v
    elif isinstance(value, dict):
        for param, v in value:
            build_args["params"][param] = v
    else:
        p = next(iter(build_args["params"]))
        build_args["params"][p] = value


def _find_subclass(name, base_class):

    for c in base_class.__subclasses__():
        if c.__name__ == name:
            return c
        else:
            sc = _find_subclass(name, c)
            if sc:
                return sc

class BondGraphBase:
    def __init__(self, name, parent=None,
                 ports=None, params=None):
        """
        Base class definition for all bond graphs.

        Args:
            name: Assumed to be unique
            metadata (dict):
        """
        #super().__init__(name, parent)
        self.name = name
        self._ports = ports
        """ List of exposed Power ports"""

        """ Dictionary of internal parameter and their values. The key is 
        the internal parameter, the value may be an exposed control value,
        a function of time, or a constant."""
        self.view = None

    @property
    def ports(self):
        return self._ports

    @property
    def state_vars(self):
        return NotImplementedError

    @property
    def control_vars(self):
        return NotImplementedError

    @property
    def params(self):
        raise NotImplementedError

    @property
    def basis_vectors(self):
        raise NotImplementedError

    def connect_port(self, port):
        pass

    def release_port(self, port):
        pass

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__



class InvalidPortException(Exception):
    pass

class InvalidComponentException(Exception):
    pass

class ModelParsingError(Exception):
    pass