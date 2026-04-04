import { createResource } from "./useFrappeFetch";
import { ref } from "vue";

export const useAdmitCard = () => {
  const loading = ref(false);
  const error = ref(null);
  const data = ref([]);

  // fetchAdmit now accepts exam_type as a parameter
  const fetchAdmit = async (exam_type = "") => {
    loading.value = true;
    error.value = null;

    try {
      const resource = createResource({
        url: "vidyaan.api_folder.exam.get_admit_data",
        params: { exam_type },
      });

      const res = await resource.fetch();
      console.log("Fetched Admit Data:", res);
      data.value = res;
    } catch (err) {
      console.error("Failed to load exams:", err);
      error.value = err.message || "Unknown error";
    } finally {
      loading.value = false;
    }
  };

  return { data, loading, error, fetchAdmit };
};