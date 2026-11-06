
"""Conference room and equipment scheduler with basic input validation."""

import json
from datetime import datetime
from pathlib import Path

reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
next_reservation = 1


def validate_time_slot(time_slot):
    """Validate a time slot written as start-end, using 24-hour hours."""
    if not isinstance(time_slot, str) or "-" not in time_slot:
        raise ValueError("Time slot must be a string like '10-12'.")

    parts = time_slot.split("-")
    if len(parts) != 2:
        raise ValueError(
            "Time slot must contain one hyphen, like '10-12'."
        )

    try:
        start, end = (int(part) for part in parts)
    except ValueError as exc:
        raise ValueError("Start and end times must be whole hours.") from exc

    if not (0 <= start < 24 and 1 <= end <= 24 and start < end):
        raise ValueError(
            "Time slot must have a valid start before its end (0-24)."
        )

    return start, end


def schedule_room(room_id, time_slot, equipment_list=None):
    """Reserve a room and available equipment, rejecting invalid bookings."""
    global next_reservation

    if not isinstance(room_id, str) or not room_id.strip():
        raise ValueError("Room ID must be a non-empty string.")

    validate_time_slot(time_slot)
    requested_equipment = (
        list(equipment_list) if equipment_list is not None else []
    )

    for reservation in reservations.values():
        if reservation["room"] == room_id and reservation["slot"] == time_slot:
            message = f"{room_id} double-booked at {time_slot}"
            conflicts.append(message)
            raise ValueError(message)

    requested_counts = {}
    for item in requested_equipment:
        if item not in equipment_pool:
            raise ValueError(f"Unknown equipment: {item}")
        requested_counts[item] = requested_counts.get(item, 0) + 1

    for item, count in requested_counts.items():
        if equipment_pool[item] < count:
            raise ValueError(f"Not enough equipment available: {item}")

    for item, count in requested_counts.items():
        equipment_pool[item] -= count

    reservation_id = next_reservation
    reservations[reservation_id] = {
        "room": room_id,
        "slot": time_slot,
        "equipment": requested_equipment,
    }
    next_reservation += 1
    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its equipment; report if not found."""
    reservation = reservations.pop(reservation_id, None)
    if reservation is None:
        return False

    for item in reservation["equipment"]:
        equipment_pool[item] += 1
    return True


def slot_hours(time_slot):
    """Return the duration of a valid time slot in whole hours."""
    start, end = validate_time_slot(time_slot)
    return end - start


def export_schedule(file="schedule.json"):
    """Write reservations to a JSON file using a context manager."""
    with Path(file).open("w", encoding="utf-8") as output_file:
        json.dump(reservations, output_file, indent=2)
        output_file.write("\n")


def log_conflicts(file="conflicts.log"):
    """Append conflicts to a log and print its contents without shell calls."""
    log_path = Path(file)
    with log_path.open("a", encoding="utf-8") as output_file:
        for conflict in conflicts:
            timestamp = datetime.now().isoformat(timespec="seconds")
            output_file.write(f"{timestamp} {conflict}\n")

    if log_path.exists():
        print(log_path.read_text(encoding="utf-8"), end="")


def main():
    """Run a small demonstration of the scheduler."""
    schedule_room("Board-1", "09-11")
    try:
        schedule_room("Board-1", "09-11")
    except ValueError as error:
        print(f"Booking rejected: {error}")

    reservation_id = schedule_room("Huddle-3", "14-16")
    print("Slot length:", slot_hours(reservations[reservation_id]["slot"]))
    print("Reservation 77 cancelled:", cancel_reservation(77))

    slot = (
        input("Slot for Board-2, like 10-12 (Enter for 10-12): ").strip()
        or "10-12"
    )
    try:
        schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Could not schedule room: {error}")

    export_schedule()
    log_conflicts()
    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
