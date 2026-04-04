import { createResource } from "./useFrappeFetch";

export const useFacultyMember = () => {
    const loading = ref(false);
    const error = ref(null);
    const members = ref([])

    const fetchMember = async () => {
        ((loading.value = true), (error.value = null));
        try {
            const resource = createResource({
                url: "vidyaan.api_folder.faculty.get_all_faculty_data",
            });
            const res = await resource.fetch();
            console.log("Member Data: ",res);

            members.value = res;
        } catch (error) {
            console.error("Failed to load allExams:", error);
            error.value = error.message || "Unknown error";
        } finally {
            loading.value = false;
        }
    }
    return {loading, error, members, fetchMember}
}