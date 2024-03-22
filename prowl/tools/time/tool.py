from prowl.lib.tool import ProwlTool
from datetime import datetime, datetime, timedelta
import pytz

class TimeTool(ProwlTool):
    def __init__(self):
        super().__init__(
            name="time",
            description="Get the current system time"
        )

    async def run(self, *args, **kwargs):
        # Concatenate all arguments into a single string
        timezone = None
        if len(args) > 0:
            timezone = args[0]

        # Get the current date and time
        now = datetime.now(tz=pytz.utc)

        # Convert the time to the specified timezone if given
        if timezone:
            timezone = pytz.timezone(timezone)
            now = now.astimezone(timezone)

        # Format the time using the automatic locale
        formatted_time = now.strftime("%A, %B %d %Y (%I:%M:%S %p)")

        # Return the formatted time and metadata
        return ProwlTool.Return(formatted_time, {
            "unix_timestamp": int(now.timestamp())
        })
