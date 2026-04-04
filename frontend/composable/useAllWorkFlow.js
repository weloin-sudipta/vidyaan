import { createResource } from "./useFrappeFetch";

export const useWorkflow = () => {
    const loading = ref(false);
    const error = ref(null);
    const workflows = ref([]);

    const fetchWorkflow = async () => {
        loading.value = true;
        error.value = null;
        console.log("call");
        
        try {
            const resource = createResource({
                url: "vidyaan.api_folder.leave_application.get_all_workflow",
            });

            const res = await resource.fetch();
            console.log(res);

            workflows.value = res;

        } catch (err) {  
            error.value = err.message || 'Unknown error';
        } finally {
            loading.value = false;
        }
    };

    return { loading, error, workflows, fetchWorkflow };
};