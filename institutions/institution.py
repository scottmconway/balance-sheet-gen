import logging
from typing import Dict, Set


class Institution:
    """
    Generic base class to manage all other Institutions.
    When an Institution is created, it will become a specific type of Institution,
    based on the name parameter passed in with it.
    If no Institution exists with the provided classname,
    an AttributeError is thrown.
    """

    def __new__(cls, type_name: str, name: str, config: Dict, logger: logging.Logger):

        if cls.__name__ != "Institution":
            return super(Institution, cls).__new__(cls)

        subclasses = all_subclasses(Institution)
        for class_obj in subclasses:
            if class_obj.__name__ == type_name:
                return class_obj(type_name, name, config, logger)

        # TODO raise a custom exception here so we can address it
        raise AttributeError("Invalid class name")

    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        self.name = name
        self.config = config
        self.logger = logger

    def get_balance(self) -> int:
        """
        Given a valid configuration in __init__,
        return the balance (in USD) for this institution's account

        :return: The USD balance of the account
        :rtype: float
        """
        raise NotImplementedError()


def all_subclasses(cls) -> Set:
    """
    Returns a set of all subclasses of a class, recursively.

    :return: All subclasses of the provided class
    :rtype: Set
    """

    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
