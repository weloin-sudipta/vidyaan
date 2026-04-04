import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

export const useGrading = () => {
    // ── state (inside the factory function, not module-level)
    const plan = ref(null)
    const students = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const error = ref(null)

    // ── Fetch students + existing results for a given Assessment Plan
    const fetchExamStudents = async (assessmentPlan) => {
        if (!assessmentPlan) return

        loading.value = true
        error.value = null
        plan.value = null
        students.value = []

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_grading.get_exam_students',
            })

            const res = await resource.submit({ assessment_plan: assessmentPlan })

            plan.value = res?.plan || null

            students.value = (res?.students || []).map(s => ({
                student: s.student,
                student_name: s.student_name,
                result_id: s.result_id ?? null,
                score: s.score ?? '',
                comment: s.comment ?? '',
                grade: s.grade ?? null,
            }))

            return res
        } catch (err) {
            console.error('fetchExamStudents error:', err)
            error.value = err.message || 'Failed to load students'
        } finally {
            loading.value = false
        }
    }

    // ── Submit / update results for all students 
    const submitExamResults = async (assessmentPlan) => {
        if (!assessmentPlan || students.value.length === 0) return

        saving.value = true
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_grading.submit_exam_results',
            })

            const payload = students.value.map(s => ({
                student: s.student,
                score: s.score || 0,
                comment: s.comment || '',
            }))

            const res = await resource.submit({
                assessment_plan: assessmentPlan,
                results: JSON.stringify(payload),
            })

            // Refresh so grades + result_ids are updated from Frappe
            await fetchExamStudents(assessmentPlan)

            return res
        } catch (err) {
            console.error('submitExamResults error:', err)
            error.value = err.message || 'Failed to save results'
            throw err
        } finally {
            saving.value = false
        }
    }

    return {
        plan,
        students,
        loading,
        saving,
        error,
        fetchExamStudents,
        submitExamResults,
    }
}