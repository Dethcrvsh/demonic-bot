from __future__ import annotations
import requests
import re
from re import Match
from requests.exceptions import HTTPError
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


"""
Handle fetching and parsing of the bands schedule from TeamUp
"""

class ScheduleHandler:
    URL_BASE: str = "https://teamup.com/kst6xmys1gryd2c54b/events?startDate={start_date}&endDate={end_date}&tz=Europe%2FStockholm"
    SWEDISH_WEEKDAYS: list[str] = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
    # How far ahead the schedule should check (in weeks)
    SCHEDULE_RANGE: int = 2
    ENTRY_RE: str = '(?<="who":"Demonic Science").*?"location":"(.*?)".*?"start_dt":"(.*?)","end_dt":"(.*?)"'


    @dataclass
    class Entry:
        start: int
        end: int
        location: str


    def __init__(self) -> None:
        self.scheduled_times: list[int] = []


    def get_schedule(self) -> str:
        response: str = self._request_data()
        scheduled_times: list[Entry] = self._get_entries(response)

        return self._get_formatted_schedule(scheduled_times)


    def _create_url(self) -> str:
        """Create the url with the correct start and end dates"""
        current_date: datetime = datetime.now()

        start_date: str = current_date.strftime("%Y-%m-%d")
        end_date: str = (current_date + timedelta(weeks=self.SCHEDULE_RANGE)).strftime("%Y-%m-%d")

        return self.URL_BASE.format(start_date=start_date, end_date=end_date)


    def _request_data(self) -> str:
        """Fetch the schedule data from the TeamUp server"""
        url: str = self._create_url()
        
        try:
            response: Response = requests.get(url)
            response.raise_for_status()
            return response.text

        except HTTPError as err:
            print(err)

        return ""


    def _time_to_unix(self, time: str) -> int:
        """Parse a time from the response into unix"""
        dt_object = datetime.fromisoformat(time)
        return int(dt_object.replace(tzinfo=timezone.utc).timestamp())


    def _get_entries(self, response: str) -> list[int]:
        """Get the entries in unix time from the TeamUp response"""
        scheduled_times: list[Entry] = []

        matches: list[Match] = re.findall(self.ENTRY_RE, response)

        for location, start, end in matches:
            scheduled_times.append(self.Entry(
                self._time_to_unix(start),
                self._time_to_unix(end),
                location
            ))

        # Make sure they are sorted, they probably are already but just to be sure
        scheduled_times.sort(key=lambda x: x.start)

        return scheduled_times
    

    def _get_formatted_schedule(self, scheduled_times: list[Entry]) -> str:
        t = 3

        output: str = f":star:                  REPSCHEMA V. {t}                  :star:\n\n"
        
        for entry in scheduled_times:
            date_object_start = datetime.utcfromtimestamp(entry.start)
            date_object_end = datetime.utcfromtimestamp(entry.end)

            day: str = self.SWEDISH_WEEKDAYS[date_object_start.weekday()]
            schedule_time: str = f"{date_object_start.hour} - {date_object_end.hour}"
            location: str = entry.location

            output += f":calendar_spiral: {day}         :clock4: {schedule_time}         :house: {location}\n"

        return output


if __name__ == "__main__":
    s = ScheduleHandler()
    print(s.get_schedule())

