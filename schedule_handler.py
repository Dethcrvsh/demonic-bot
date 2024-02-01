from __future__ import annotations
import requests
import re
import json
from re import Match
from requests import Response
from requests.exceptions import HTTPError
from datetime import datetime, time, timedelta, timezone
from dataclasses import dataclass


"""
Handle fetching and parsing of the bands schedule from TeamUp
"""

class ScheduleHandler:
    URL_BASE: str = "https://teamup.com/kst6xmys1gryd2c54b/events?startDate={start_date}&endDate={end_date}&tz=Europe%2FStockholm"
    # How far ahead times should be checked
    DAYS_AHEAD = 30
    BAND_NAME: str = "Demonic Science"


    @dataclass
    class Entry:
        start: datetime
        end: datetime
        location: str
        has_sent_notification: bool = False

        def __eq__(self, other: ScheduleHandler.Entry) -> bool:
            return (
                self.start == other.start and
                self.end == other.end and
                self.location == other.location
            )


    def __init__(self) -> None:
        self.scheduled_times: list[ScheduleHandler.Entry] = []


    def get_schedule(self) -> str:
        response: str = self._request_data()

        if not response:
            return "Could not fetch data from TeamUp."

        self._add_new_entries(response)

        return self._get_formatted_schedule(self.scheduled_times)


    def get_notifications(self) -> str:
        return self._get_new_times_notifications()


    def _create_url(self) -> str:
        """Create the url with the correct start and end dates"""
        current_date: datetime = datetime.now()

        start_date: str = current_date.strftime("%Y-%m-%d")
        # Only fetch the schedule weekly
        end_date = current_date + timedelta(days=self.DAYS_AHEAD)

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


    def _add_new_entries(self, response: str):
        """Get the entries in unix time from the TeamUp response"""

        try:
            data = json.loads(response)
        except json.JSONDecodeError as err:
            print(err)
            return

        new_scheduled_times: list[ScheduleHandler.Entry] = []

        # Move over the existing schedules to the new ones
        for e in data["events"]:
            if not e["who"].lower() == self.BAND_NAME.lower():
                continue

            new_entry: ScheduleHandler.Entry = self.Entry(
                self._time_to_datetime(e["start_dt"]),
                self._time_to_datetime(e["end_dt"]),
                e["location"]
            )

            if new_entry in self.scheduled_times:
                new_scheduled_times += [self.scheduled_times[self.scheduled_times.index(new_entry)]]
            else:
                new_scheduled_times += [new_entry]

        self.scheduled_times = new_scheduled_times
    
    
    def _get_new_times_notifications(self, ) -> str:
        """Compare a new list of scheduled times to the old one and return the new ones"""

        output: str = ""

        for e in self.scheduled_times:
            if e.has_sent_notification:
                continue

            day: str = self._get_day(e.start)

            output += f":exclamation: Ett nytt rep har lagts till {'på' if len(day) > 5 else 'den'} {day} i {self._get_location(e.location)}\n"
            e.has_sent_notification = True

        return output


    def _get_day(self, date: datetime) -> str:
        """Get the weekday or the date from a datetime depending on how much time is left"""

        SWEDISH_WEEKDAYS: list[str] = [
            "Måndag",
            "Tisdag",
            "Onsdag",
            "Torsdag",
            "Fredag",
            "Lördag",
            "Söndag"
        ]

        # Display the date instead of weekdays if its more than one week ahead
        if date - datetime.now().astimezone(timezone.utc) < timedelta(weeks=1):
            return SWEDISH_WEEKDAYS[date.weekday()] 
        else:
            return date.strftime("%d/%m")

    def _get_location(self, location: str) -> str:
        """Get the correctly formatted location"""
        number: str = "".join(filter(lambda c: c.isdigit(), location))
        return "Lokal " +  number if number else "-"
    

    def _get_formatted_schedule(self, scheduled_times: list[Entry]) -> str:

        output: str = f":star:                  REPSCHEMA                  :star:\n\n\n"
        
        for entry in scheduled_times:
            day: str = self._get_day(entry.start)
            schedule_time: str = f"{entry.start.hour} - {entry.end.hour}"
            location: str = self._get_location(entry.location)

            output += f":calendar_spiral: {day}         :clock4: {schedule_time}         :house: {location}\n"
        
        output += f"\n\n\n\n*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return output


if __name__ == "__main__":
    s = ScheduleHandler()
    pass

