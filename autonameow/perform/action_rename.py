# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
from perform.action_abstract import AbstractAction


class RenameAction(AbstractAction):

    def __init__(self, file_object, results):
        super(RenameAction, self).__init__(file_object, results)

    def perform_action(self):
        pass

