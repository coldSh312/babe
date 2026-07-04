"""
models.py
=========

Data models and business logic for the patient attendance tracking application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

DATE_FORMAT = "%d/%m/%Y"


class InvalidDateError(ValueError):
    """Raised when a date string does not match the expected DD/MM/YYYY format."""


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise InvalidDateError(
            f"'{date_str}' is not a valid date. Expected format: DD/MM/YYYY"
        ) from exc


class ClinicData:
    def __init__(
        self,
        patients: Optional[List[str]] = None,
        dates: Optional[List[str]] = None,
        attendance: Optional[Dict[str, Dict[str, bool]]] = None,
        price_per_session: float = 0.0,
        default_month: Optional[int] = None,
        default_year: Optional[int] = None,
    ) -> None:
        self.patients: List[str] = list(patients) if patients else []
        self.dates: List[str] = list(dates) if dates else []
        self.attendance: Dict[str, Dict[str, bool]] = (
            {p: dict(d) for p, d in attendance.items()} if attendance else {}
        )
        self.price_per_session: float = price_per_session
        
        now = datetime.now()
        self.default_month: int = default_month if default_month is not None else now.month
        self.default_year: int = default_year if default_year is not None else now.year

        self._sort_dates()
        self._ensure_attendance_integrity()

    def to_dict(self) -> dict:
        return {
            "patients": self.patients,
            "dates": self.dates,
            "attendance": self.attendance,
            "price_per_session": self.price_per_session,
            "default_month": self.default_month,
            "default_year": self.default_year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClinicData":
        return cls(
            patients=data.get("patients", []),
            dates=data.get("dates", []),
            attendance=data.get("attendance", {}),
            price_per_session=data.get("price_per_session", 0.0),
            default_month=data.get("default_month"),
            default_year=data.get("default_year"),
        )

    def _sort_dates(self) -> None:
        try:
            self.dates.sort(key=parse_date)
        except InvalidDateError:
            pass

    def _ensure_attendance_integrity(self) -> None:
        for patient in self.patients:
            self.attendance.setdefault(patient, {})
            for date in self.dates:
                self.attendance[patient].setdefault(date, False)

    # ---- Patient management ----
    def add_patient(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("שם המטופל לא יכול להיות ריק")
        if name in self.patients:
            raise ValueError(f"מטופל בשם '{name}' כבר קיים")
        self.patients.append(name)
        self.attendance[name] = {date: False for date in self.dates}

    def remove_patient(self, name: str) -> None:
        if name not in self.patients:
            raise ValueError(f"מטופל בשם '{name}' לא נמצא")
        self.patients.remove(name)
        self.attendance.pop(name, None)

    def rename_patient(self, old_name: str, new_name: str) -> None:
        new_name = new_name.strip()
        if old_name not in self.patients:
            raise ValueError(f"מטופל בשם '{old_name}' לא נמצא")
        if not new_name:
            raise ValueError("שם המטופל לא יכול להיות ריק")
        if new_name != old_name and new_name in self.patients:
            raise ValueError(f"מטופל בשם '{new_name}' כבר קיים")

        index = self.patients.index(old_name)
        self.patients[index] = new_name
        self.attendance[new_name] = self.attendance.pop(old_name)

    # ---- Date management ----
    def add_date(self, date_str: str) -> None:
        date_str = date_str.strip()
        parse_date(date_str)
        if date_str in self.dates:
            return  # Fail silently if date already exists (good for bulk entry)
        self.dates.append(date_str)
        self._sort_dates()
        for patient in self.patients:
            self.attendance[patient][date_str] = False

    def remove_date(self, date_str: str) -> None:
        if date_str not in self.dates:
            raise ValueError(f"התאריך '{date_str}' לא נמצא")
        self.dates.remove(date_str)
        for patient in self.patients:
            self.attendance[patient].pop(date_str, None)

    def rename_date(self, old_date: str, new_date: str) -> None:
        new_date = new_date.strip()
        if old_date not in self.dates:
            raise ValueError(f"התאריך '{old_date}' לא נמצא")
        parse_date(new_date)
        if new_date != old_date and new_date in self.dates:
            raise ValueError(f"התאריך '{new_date}' כבר קיים")

        index = self.dates.index(old_date)
        self.dates[index] = new_date
        for patient in self.patients:
            self.attendance[patient][new_date] = self.attendance[patient].pop(old_date)
        self._sort_dates()

    # ---- Attendance & Calculations ----
    def toggle_attendance(self, patient: str, date: str) -> bool:
        current = self.attendance.setdefault(patient, {}).get(date, False)
        new_value = not current
        self.attendance[patient][date] = new_value
        return new_value

    def is_present(self, patient: str, date: str) -> bool:
        return self.attendance.get(patient, {}).get(date, False)

    def get_patient_total(self, patient: str) -> int:
        return sum(1 for present in self.attendance.get(patient, {}).values() if present)
        
    def get_date_total(self, date_str: str) -> int:
        """Return total sessions across all patients for a specific date."""
        return sum(1 for p in self.patients if self.is_present(p, date_str))

    def get_grand_total(self) -> int:
        return sum(self.get_patient_total(p) for p in self.patients)

    def get_total_income(self) -> float:
        return self.get_grand_total() * self.price_per_session