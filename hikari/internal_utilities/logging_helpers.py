#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
"""
Utilities for logging tools.
"""
import inspect
import logging
import typing
import uuid


def get_named_logger(obj: typing.Optional[typing.Any] = None, *extras: typing.Any) -> logging.Logger:
    """
    Builds an appropriately named logger. If called with no arguments or with `NoneType`, the current module is used
    to produce the name. If this is run from a location where no module info is available, a random UUID is used
    instead.

    If the passed object is an instance of a class, the class is used instead.

    If a class is provided/used, then the fully qualified package and class name is used to name the logger.

    If a string is provided, then the string is used as the name. This is not recommended.

    Args:
        obj:
            the object to study to produce a logger for.
        extras:
            optional extra components to add to the end of the logger name.

    Returns:
        a created logger.
    """
    try:
        if obj is None:
            obj = inspect.getmodule(inspect.stack()[1][0])

            # No module was found... maybe we are in an interactive session or some compiled module?
            if obj is None:
                raise AttributeError
            else:
                obj = obj.__name__
        elif not isinstance(obj, str):
            if not isinstance(obj, type):
                obj = type(obj)

            obj = f"{obj.__module__}.{obj.__qualname__}"
    except AttributeError:
        obj = str(uuid.uuid4())
    finally:
        if extras:
            extras = ", ".join(map(str, extras))
            obj = f"{obj}[{extras}]"

        return logging.getLogger(obj)