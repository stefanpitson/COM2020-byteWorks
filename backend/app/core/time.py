from datetime import datetime, timedelta, timezone 

class OurTime:
    def __init__(self, offset_days=0, offset_hours=0):
        self.offset_days = offset_days
        self.offset_hours = offset_hours

    def now(self, zone: timezone):
        return datetime.now(zone) -timedelta(days=self.offset_days,hours=self.offset_hours)

    def date(self):
        return (datetime.now() - timedelta(days=self.offset_days)).date()
    
    def time(self):
        # Always subtract from datetime first, then extract .time()
        return (datetime.now() - timedelta(hours=self.offset_hours)).time()
    
    def set_day(self, i:int):
        self.offset_days

    def set_hours(self, i:int):
        self.offset_hours

timer = OurTime(offset_days=0, offset_hours=0)