import re
from typing import Dict, Iterable, Optional

from django.db.models import Q

from bookings.models import Booking
from core.utils import haversine_km
from services.models import ServiceCategory, WorkerProfile

SERVICE_KEYWORDS = {
    "AC Technician": [
        "ac", "air conditioner", "aircon", "cooling", "not cooling", "ac not cooling",
        "ac making noise", "compressor", "blower", "cooling issue"
    ],
    "Plumber": [
        "water pipe", "pipe leaking", "tap leaking", "leak", "leaking", "plumbing",
        "toilet overflow", "drain block", "water leakage", "tap", "pipe"
    ],
    "Electrician": [
        "fan not working", "switch problem", "switch", "light not working", "socket",
        "electrical", "wiring", "circuit", "power issue", "fan", "bulb"
    ],
    "Carpenter": [
        "door broken", "window jammed", "cabinet", "wooden", "furniture", "door repair",
        "table", "lock repair", "wood work"
    ],
    "Cleaner": [
        "house cleaning", "cleaning", "deep cleaning", "mop", "dust", "kitchen cleaning",
        "home cleaning", "office cleaning", "bathroom cleaning"
    ],
    "Gardener": [
        "garden maintenance", "garden", "lawn", "grass", "planting", "watering", "pruning",
        "landscaping", "flower bed"
    ],
    "Solar Technician": [
        "solar pump", "solar panel", "solar maintenance", "solar not working", "pv panel",
        "solar inverter", "solar pump not working"
    ],
    "Pump Technician": [
        "water pump", "pump not working", "motor pump", "borewell", "submersible pump",
        "pump failure", "water supply pump"
    ],
    "Agricultural Technician": [
        "farm equipment", "tractor", "harvester", "agricultural", "farm machinery",
        "cultivator", "dairy equipment", "agri machine", "equipment problem"
    ],
    "Technician": [
        "appliance", "refrigerator", "washing machine", "microwave", "device", "repair",
        "machine not working", "home appliance"
    ],
}


def extract_service_requirements(problem_text: str) -> list[str]:
    if not problem_text or not problem_text.strip():
        return []

    normalized = normalize_problem(problem_text)
    matches = []

    for service_name, keywords in SERVICE_KEYWORDS.items():
        positions = [normalized.find(keyword) for keyword in keywords if keyword in normalized]
        if positions:
            matches.append((min(positions), service_name))

    if not matches:
        return ["Technician"]

    ordered = [service_name for _, service_name in sorted(matches, key=lambda item: item[0])]
    unique = []
    for service_name in ordered:
        if service_name not in unique:
            unique.append(service_name)
    return unique


def normalize_problem(problem_text: str) -> str:
    normalized = problem_text.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def classify_problem(problem_text: str) -> str:
    requirements = extract_service_requirements(problem_text)
    return requirements[0] if requirements else "Technician"


def compute_match_score(candidate: Dict) -> float:
    skill = max(0.0, float(candidate.get("skill_match", 0)))
    distance_km = float(candidate.get("distance_km", 9999))
    availability = 1 if candidate.get("availability") else 0
    rating = float(candidate.get("rating", 0))
    experience = float(candidate.get("experience_years", 0))
    response_minutes = float(candidate.get("response_minutes", 60))
    workload = float(candidate.get("workload", 0))

    distance_score = max(0.0, 100.0 - (distance_km * 8.0))
    rating_score = (rating / 5.0) * 100.0
    experience_score = min(100.0, experience * 10.0)
    response_score = max(0.0, 100.0 - (response_minutes * 2.0))
    workload_penalty = min(20.0, workload * 0.8)

    score = (
        skill * 0.35
        + distance_score * 0.20
        + availability * 100.0 * 0.15
        + rating_score * 0.10
        + experience_score * 0.10
        + response_score * 0.10
    ) - workload_penalty * 0.15

    return round(max(0.0, min(100.0, score)), 1)


def _worker_workload(profile: WorkerProfile) -> int:
    return Booking.objects.filter(
        worker=profile.user,
        status__in=[Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS, Booking.Status.PENDING, Booking.Status.COMPLETED],
    ).count()


def _recommend_for_single_service(service_name: str, customer_lat: float, customer_lng: float):
    category = ServiceCategory.objects.filter(name=service_name).first()
    if not category:
        category = ServiceCategory.objects.filter(is_active=True).first()

    workers = WorkerProfile.objects.filter(service_categories=category, is_verified=True).select_related("user")
    workers = workers.filter(user__is_active=True)

    candidates = []
    for profile in workers:
        if profile.latitude is None or profile.longitude is None:
            distance = 9999
        else:
            distance = haversine_km(customer_lat, customer_lng, profile.latitude, profile.longitude) or 9999

        availability = 1 if profile.is_online else 0
        if availability == 0:
            continue

        workload = _worker_workload(profile)
        response_minutes = 15 + max(2, int(distance * 8))
        skill_match = 100 if profile.service_categories.filter(name=service_name).exists() else 85
        candidate = {
            "profile": profile,
            "distance_km": distance,
            "availability": availability,
            "rating": float(profile.rating_avg or 0),
            "experience_years": int(profile.experience_years or 0),
            "response_minutes": response_minutes,
            "workload": workload,
            "skill_match": skill_match,
            "service_name": service_name,
        }
        candidate["score"] = compute_match_score(candidate)
        candidates.append(candidate)

    if not candidates:
        backup = WorkerProfile.objects.filter(service_categories=category, is_verified=True).select_related("user").first()
        if backup is None:
            return {"service_name": service_name, "category": category, "worker": None, "candidates": []}
        candidate = {
            "profile": backup,
            "distance_km": 9999,
            "availability": 0,
            "rating": float(backup.rating_avg or 0),
            "experience_years": int(backup.experience_years or 0),
            "response_minutes": 60,
            "workload": _worker_workload(backup),
            "skill_match": 80,
            "service_name": service_name,
        }
        candidate["score"] = compute_match_score(candidate)
        candidates.append(candidate)

    candidates.sort(key=lambda item: (-item["score"], item["distance_km"], item["workload"]))
    return {"service_name": service_name, "category": category, "worker": candidates[0], "candidates": candidates[:5]}


def recommend_worker_for_problem(problem_text: str, customer_lat: Optional[float] = None, customer_lng: Optional[float] = None):
    service_requirements = extract_service_requirements(problem_text)
    if customer_lat is None:
        customer_lat = 23.0225
    if customer_lng is None:
        customer_lng = 72.5714

    service_results = []
    for service_name in service_requirements:
        service_results.append(_recommend_for_single_service(service_name, customer_lat, customer_lng))

    primary = service_results[0] if service_results else {
        "service_name": classify_problem(problem_text),
        "category": ServiceCategory.objects.filter(is_active=True).first(),
        "worker": None,
        "candidates": [],
    }

    return {
        "service_name": primary["service_name"],
        "service_names": [item["service_name"] for item in service_results],
        "category": primary["category"],
        "worker": primary["worker"],
        "workers_by_service": service_results,
        "candidates": primary["candidates"],
        "has_multiple_services": len(service_results) > 1,
    }
