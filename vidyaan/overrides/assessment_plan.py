import frappe
from education.education.doctype.assessment_plan.assessment_plan import AssessmentPlan

class VidyaanAssessmentPlan(AssessmentPlan):
	def validate_overlap(self):
		"""Validates overlap ONLY for Assessment Plans, skipping Course Schedules."""

		from education.education.utils import validate_overlap_for

		# SKIP: validate overlapping course schedules (User requirement)
		# We bypass these checks to allow overlapping with existing class schedules.
		# if self.student_group:
		# 	validate_overlap_for(self, "Course Schedule", "student_group")
		# validate_overlap_for(self, "Course Schedule", "instructor")
		# validate_overlap_for(self, "Course Schedule", "room")

		# validate overlapping assessment schedules (Keep this for internal consistency)
		if self.student_group:
			validate_overlap_for(self, "Assessment Plan", "student_group")

		validate_overlap_for(self, "Assessment Plan", "room")
		validate_overlap_for(self, "Assessment Plan", "supervisor", self.supervisor)
