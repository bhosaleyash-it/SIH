from django.test import TestCase

from core.autopilot import classify_problem, compute_match_score, extract_service_requirements


class ServiceAutopilotTests(TestCase):
    def test_classify_problem_maps_common_faults_to_services(self):
        self.assertEqual(classify_problem("My AC is not cooling."), "AC Technician")
        self.assertEqual(classify_problem("water pipe leaking"), "Plumber")
        self.assertEqual(classify_problem("fan not working"), "Electrician")
        self.assertEqual(classify_problem("house cleaning"), "Cleaner")

    def test_match_score_prefers_lower_workload_and_closer_worker(self):
        first = {
            "rating": 4.9,
            "distance_km": 7,
            "workload": 20,
            "availability": 1,
            "experience_years": 8,
            "response_minutes": 25,
            "skill_match": 95,
        }
        second = {
            "rating": 4.7,
            "distance_km": 2,
            "workload": 5,
            "availability": 1,
            "experience_years": 5,
            "response_minutes": 18,
            "skill_match": 90,
        }
        self.assertGreater(compute_match_score(second), compute_match_score(first))

    def test_extract_service_requirements_handles_multiple_services_in_single_problem(self):
        requirements = extract_service_requirements("fan not working and water pipe is leaking in the bathroom")
        self.assertEqual(requirements, ["Electrician", "Plumber"])
