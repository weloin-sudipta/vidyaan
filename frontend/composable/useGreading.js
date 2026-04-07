import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

export const useGrading = () => {
    // ── state ────────────────────────────────────────────────────────────────
    const plan = ref(null)
    const students = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const savingStudent = ref(null)   // student id currently being saved (per-row spinner)
    const error = ref(null)

    // ── Fetch students + existing results for a given Assessment Plan ────────
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
                docstatus: s.docstatus ?? null,   // 0 = draft, 1 = submitted, null = none
            }))

            return res
        } catch (err) {
            console.error('fetchExamStudents error:', err)
            error.value = err.message || 'Failed to load students'
        } finally {
            loading.value = false
        }
    }

    // ── Submit / update results for ALL students in the table ───────────────
    // submit=true → docstatus 1 (final). submit=false → save as draft.
    const submitExamResults = async (assessmentPlan, { submit = true } = {}) => {
        if (!assessmentPlan || students.value.length === 0) return

        saving.value = true
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_grading.submit_exam_results',
            })

            // Skip rows with blank score — don't create empty drafts
            const payload = students.value
                .filter(s => s.score !== '' && s.score !== null && s.score !== undefined)
                .map(s => ({
                    student: s.student,
                    score: s.score,
                    comment: s.comment || '',
                }))

            if (payload.length === 0) {
                error.value = 'Enter at least one score before submitting'
                return { success: false, saved_count: 0, errors: [] }
            }

            const res = await resource.submit({
                assessment_plan: assessmentPlan,
                results: JSON.stringify(payload),
                submit: submit ? 1 : 0,
            })

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

    // ── Save / submit a SINGLE student row ──────────────────────────────────
    const saveSingleResult = async (assessmentPlan, student, { submit = true } = {}) => {
        if (!assessmentPlan || !student?.student) return
        if (student.score === '' || student.score === null || student.score === undefined) {
            error.value = 'Score is required'
            return { success: false }
        }

        savingStudent.value = student.student
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_grading.submit_single_result',
            })

            const res = await resource.submit({
                assessment_plan: assessmentPlan,
                student: student.student,
                score: student.score,
                comment: student.comment || '',
                submit: submit ? 1 : 0,
            })

            // Patch the local row from the server response (avoids full refetch)
            if (res?.success && res.result) {
                const idx = students.value.findIndex(s => s.student === student.student)
                if (idx !== -1) {
                    students.value[idx] = {
                        ...students.value[idx],
                        result_id: res.result.result_id,
                        grade: res.result.grade,
                        docstatus: res.result.docstatus,
                        score: res.result.total_score ?? students.value[idx].score,
                    }
                }
            } else if (res && !res.success) {
                error.value = res.error || 'Failed to save'
            }

            return res
        } catch (err) {
            console.error('saveSingleResult error:', err)
            error.value = err.message || 'Failed to save result'
            throw err
        } finally {
            savingStudent.value = null
        }
    }

    return {
        plan,
        students,
        loading,
        saving,
        savingStudent,
        error,
        fetchExamStudents,
        submitExamResults,
        saveSingleResult,
    }
}
