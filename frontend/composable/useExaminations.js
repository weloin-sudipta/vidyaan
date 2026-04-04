import { createResource } from "~/composable/useFrappeFetch";

// Direct async profile fetch (used in index.vue)
export const useExams = async () => {
  const examResource = createResource({
    url: "vidyaan.api_folder.exam.get_exams",
  });
  const exams = await examResource.submit();
  return exams;
};

export const useExamResults = async () => {
  const resultResource = createResource({
    url: "vidyaan.api_folder.exam.get_results",
  });
  const results = await resultResource.submit();
  return results;
};

export const useExamination = () => {
  const loading = ref(false);
  const error = ref(null);
  const exams = ref([]);
  const results = ref([]);

  const fetchExams = async () => {
    ((loading.value = true), (error.value = null));
    try {
      const resource = createResource({
        url: "vidyaan.api_folder.exam.get_exams",
      });
      const res = await resource.fetch();
      console.log(res);

      exams.value = res;
    } catch (err) {
      console.error("Failed to load allExams:", err);
      error.value = err.message || "Unknown error";
    } finally {
      loading.value = false;
    }
  };

  const fetchResults = async () => {
    ((loading.value = true), (error.value = null));
    try {
      const resource = createResource({
        url: "vidyaan.api_folder.exam.get_results",
      });
      const res = await resource.fetch();
      console.log(res);

      results.value = res;
    } catch (err) {
      console.error("Failed to load results:", err);
      error.value = err.message || "Unknown error";
    } finally {
      loading.value = false;
    }
  };

  return { loading, error, exams, fetchExams, results, fetchResults}
};
