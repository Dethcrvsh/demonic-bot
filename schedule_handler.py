from __future__ import annotations
import requests
import re
from re import Match
from requests import Response
from requests.exceptions import HTTPError
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


"""
Handle fetching and parsing of the bands schedule from TeamUp
"""

class ScheduleHandler:
    URL_BASE: str = "https://teamup.com/kst6xmys1gryd2c54b/events?startDate={start_date}&endDate={end_date}&tz=Europe%2FStockholm"
    SWEDISH_WEEKDAYS: list[str] = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
    ENTRY_RE: str = '(?<="who":"Demonic Science").*?"location":"(.*?)".*?"start_dt":"(.*?)","end_dt":"(.*?)"'


    @dataclass
    class Entry:
        start: datetime
        end: datetime
        location: str


    def __init__(self) -> None:
        self.scheduled_times: list[int] = []


    def get_schedule(self) -> tuple[str, str]:
        response: str = self._request_data()
        scheduled_times: list[ScheduleHandler.Entry] = self._get_entries(response)

        new_times: list[ScheduleHandler.Entry] = self._get_new_times(scheduled_times)

        print (self._get_notifications(new_times))

        self.scheduled_times = scheduled_times

        return self._get_formatted_schedule(scheduled_times)


    def _create_url(self) -> str:
        """Create the url with the correct start and end dates"""
        current_date: datetime = datetime.now()

        num_of_weekdays: int = 7
        days_to_sunday: int = num_of_weekdays - current_date.weekday() - 1

        start_date: str = current_date.strftime("%Y-%m-%d")
        # Only fetch the schedule weekly
        end_date = current_date + timedelta(days=days_to_sunday)

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


    def _time_to_datetime(self, time: str) -> datetime:
        """Parse a time from the response into unix"""
        dt_object = datetime.fromisoformat(time)
        return dt_object.replace(tzinfo=timezone.utc)


    def _get_entries(self, response: str) -> list[int]:
        """Get the entries in unix time from the TeamUp response"""
        scheduled_times: list[ScheduleHandler.Entry] = []

        matches: list[Match] = re.findall(self.ENTRY_RE, response)

        for location, start, end in matches:
            scheduled_times.append(self.Entry(
                self._time_to_datetime(start),
                self._time_to_datetime(end),
                location
            ))

        # Make sure they are sorted, they probably are already but just to be sure
        scheduled_times.sort(key=lambda x: x.start.timestamp())

        return scheduled_times
    
    
    def _get_new_times(self, new_scheduled_times: list[ScheduleHandler.Entry]) -> list[ScheduleHandler.Entry]:
        """Compare a new list of scheduled times to the old one and return the new ones"""

        return [e for e in new_scheduled_times if e not in self.scheduled_times]
    
    
    def _get_notifications(self, scheduled_times: list[ScheduleHandler.Entry]) -> str:
        """Create notifications from newly added schedules"""
        
        return "".join(
            f":exclamation: Ett nytt rep har lagts till {e.start.hour} - {e.end.hour} i {e.location}" 
            for e in scheduled_times
        )
    

    def _get_formatted_schedule(self, scheduled_times: list[Entry]) -> str:
        t = 3

        output: str = f":star:                  REPSCHEMA V. {t}                  :star:\n\n\n"
        
        for entry in scheduled_times:

            day: str = self.SWEDISH_WEEKDAYS[entry.start.weekday()]
            schedule_time: str = f"{entry.start.hour} - {entry.end.hour}"
            location: str = entry.location

            output += f":calendar_spiral: {day}         :clock4: {schedule_time}         :house: {location}\n"
        
        output += f"\n\n\n\n*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return output


if __name__ == "__main__":

    e1 = ScheduleHandler.Entry(1, 2, "a")
    e2 = ScheduleHandler.Entry(1, 3, "a")

    print(e1 == e2)
    s = ScheduleHandler()

