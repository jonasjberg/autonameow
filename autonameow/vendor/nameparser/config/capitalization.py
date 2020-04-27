# -*- coding: utf-8 -*-
from __future__ import unicode_literals

CAPITALIZATION_EXCEPTIONS = (
    ('ii' ,'II'),
    ('iii','III'),
    ('iv' ,'IV'),
    ('md' ,'M.D.'),
    ('phd','Ph.D.'),

    # NOTE(jonas): Added to make autonameow unit tests written for v1.0.0 pass.
    ('van', 'van'),
    ('von', 'von'),
)
"""
Any pieces that are not capitalized by capitalizing the first letter.
"""