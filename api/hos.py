from datetime import datetime, timedelta

def generate_hos_schedule(start_time: datetime, drive_hours: float, pickup=True, dropoff=True):
    """
    Very simplified HOS scheduler:
    - Max 11h driving per day
    - 30 min break after 8h driving
    - 1h pickup + 1h dropoff if enabled
    """
    timeline = []
    t = start_time

    # Pickup
    if pickup:
        timeline.append({"status": "OnDuty", "start": t.strftime("%H:%M")})
        t += timedelta(hours=1)
        timeline[-1]["end"] = t.strftime("%H:%M")
        timeline[-1]["location"] = "Pickup"

    # Driving with break
    hours_driven = 0
    while drive_hours > 0:
        if hours_driven == 8:  # force break
            timeline.append({"status": "OffDuty", "start": t.strftime("%H:%M")})
            t += timedelta(minutes=30)
            timeline[-1]["end"] = t.strftime("%H:%M")
            timeline[-1]["location"] = "Break"
            hours_driven = 0  # reset driving clock

        drive_chunk = min(drive_hours, 11 - hours_driven)
        timeline.append({"status": "Driving", "start": t.strftime("%H:%M")})
        t += timedelta(hours=drive_chunk)
        timeline[-1]["end"] = t.strftime("%H:%M")
        timeline[-1]["location"] = "On Route"

        hours_driven += drive_chunk
        drive_hours -= drive_chunk

    # Dropoff
    if dropoff:
        timeline.append({"status": "OnDuty", "start": t.strftime("%H:%M")})
        t += timedelta(hours=1)
        timeline[-1]["end"] = t.strftime("%H:%M")
        timeline[-1]["location"] = "Dropoff"

    # Rest of day = OffDuty
    timeline.append({"status": "OffDuty", "start": t.strftime("%H:%M"),
                     "end": "24:00", "location": "Rest"})

    return timeline
