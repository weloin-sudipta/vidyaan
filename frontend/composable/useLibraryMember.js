import { ref } from "vue";
import { createResource } from "./useFrappeFetch";

export const useLibraryMember = () => {
    const loading = ref(false);
    const error = ref(null);
    const memberData = ref([]);

    const fetchMemberData = async () => {
        loading.value = true;
        error.value = null;

        try {
            const resource = createResource({
                url: "vidyaan.library.api.get_member_details",
            });

            const res = await resource.fetch();

            memberData.value = res;

            console.log("Clean data:", memberData.value);

        } catch (err) {
            error.value = err.message || "Unknown error";
        } finally {
            loading.value = false;
        }
    };

    return { loading, error, memberData, fetchMemberData };
};