# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

from core import event


def set_global_configuration(active_config):
    """
    Sets the currently active configuration by dispatching an event.

    Passes 'active_config' to all callables that has been added to the
    'on_config_changed' event handler.  It is up to these callables to
    keep local state in sync with any changes to the configuration.

    Args:
        active_config: The new global config as an instance of 'Configuration'.
    """
    event.dispatcher.on_config_changed(config=active_config)
