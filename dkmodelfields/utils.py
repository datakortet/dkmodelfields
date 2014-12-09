# -*- coding: utf-8 -*-

"""In its own module to prevent circular dependencies.
"""

import re
from datetime import timedelta


def xstr_to_timedelta(td_str):
    """Returns a timedelta parsed from the native string output of a timedelta.

       Timedelta displays in the format ``X day(s), H:MM:SS.ffffff``
       Both the days section and the microseconds section are optional
       and ``days`` is singular in cases where there is only one day.

       Additionally will handle user input in months and years,
       translating those bits into a count of days which is 'close
       enough'.
    """
    if not td_str:
        return None

    time_matcher = re.compile(r"""
        (?:
            (?P<weeks>\d+)
            \W*
            (?:weeks?|w),?
        )?
        \W*
        (?:
            (?P<days>\d+)
            \W*
            (?:days?|d),?
        )?
        \W*
        (?:
            (?P<hours>\d+):
            (?P<minutes>\d+)
            (?::(?P<seconds>\d+)
            (?:\.(?P<microseconds>\d+))?)?
        )?
        """, re.VERBOSE)
    time_matches = time_matcher.match(td_str)
    time_groups = time_matches.groupdict()

    for key in time_groups.keys():
        if time_groups[key]:
            time_groups[key] = int(time_groups[key])
        else:
            time_groups[key] = 0

    time_groups["days"] = time_groups["days"] + (time_groups["weeks"] * 7)

    res = timedelta(
        days=time_groups["days"],
        hours=time_groups["hours"],
        minutes=time_groups["minutes"],
        seconds=time_groups["seconds"],
        microseconds=time_groups["microseconds"])

    return res
