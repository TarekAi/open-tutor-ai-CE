<script lang="ts">
    // ==== Components ====
    import AddClassModal from '$lib/components/teacher/element/AddClassModal.svelte';
    import AddStudentModal from '$lib/components/teacher/element/AddStudentModal.svelte';
    import ConfirmModal from '$lib/components/teacher/element/ConfirmModal.svelte';

    // ====== Utils ====
    import { onMount, getContext } from 'svelte';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { toast } from 'svelte-sonner';
    import type { Writable } from 'svelte/store';
    import { getMyClasses, createNewClass, deleteClassById, updateClass } from '$lib/apis/classe'; 
    import type { ClasseResponse } from '$lib/apis/classe';

    // ==== Languages ====
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    // ==== Variables ====
    let classes: ClasseResponse[] = [];
    let loading = true;
    let showAddClassModal: boolean = false;
    let showAddStudentModal: boolean = false;
    let selectedClassId: string | null = null;
    let selectedClassData: ClasseResponse | null = null;
    let showMoreDropdown: string | null = null;

    let showDeleteModal = false;
    let classToDelete:string |null = null;
    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    function goToClass(id: string) {
        goto(`/teacher/Classes/c/${id}`);
    }

    // ==== UI ==== 
    function closeAllDropdowns(): void {
        showMoreDropdown = null;
    }
    function toggleAddClassModal(): void {
        if (!showAddClassModal) {
            selectedClassId = null;
            selectedClassData = null;
        }
        showAddClassModal = !showAddClassModal;
        closeAllDropdowns();
    }
    function toggleMoreDropdown(id: string): void {
        showMoreDropdown = showMoreDropdown === id ? null : id;
    }
    function openAddStudentModal(classId: string): void {
        selectedClassId = classId;
        selectedClassData = null; 
        showAddStudentModal = true;
        closeAllDropdowns();
    }

    // ======== API CLASSE ========
    async function loadClasses() {
        const token = getToken();
        if (!token) return;
        loading = true;
        try {
            classes = await getMyClasses(token);
        } catch (err: any) {
            console.error("Erreur fetching classes:", err);
            toast.error($i18n.t('Failed to load classes'));
        } finally {
            loading = false;
        }
    }

    async function SaveClass(event: CustomEvent<{name: string, course: string}>){
        const classData = event.detail;
        const token = getToken();
        if (!token) {
            toast.error($i18n.t('Session expired, please login again'));
            return;
        }
        try {
            if (selectedClassId) {
                await updateClass(token, selectedClassId, classData);
                toast.success($i18n.t('Class updated successfully'));
            } else {
                await createNewClass(token, classData);
                toast.success($i18n.t('Class created successfully'));
            }
            await loadClasses(); 
            showAddClassModal = false;
            selectedClassId = null;
            selectedClassData = null;
        } catch (err: any) {
            console.error(err);
            toast.error($i18n.t('Error saving class'));
        }
    }
// Delete Class
    function DeleteClass(classId: string) {
        classToDelete = classId;
        showDeleteModal = true;
    }

    async function confirmDelete() {
    if (!classToDelete) return;
    try {
        const token = getToken();
         await deleteClassById(token, classToDelete);
         classes = classes.filter(c => c.id !== classToDelete);
        toast.success($i18n.t('Class deleted successfully'));
        showDeleteModal = false;
        classToDelete = null;

    } catch (err) {
        toast.error($i18n.t('Error during deletion'));
    }
}

// Modify Classe
    function ModifyClass(classId: string): void {
        const classe = classes.find(c => c.id === classId);
        if (classe) {
            selectedClassId = classe.id;
            selectedClassData = { ...classe }; 
            showAddClassModal = true;
            closeAllDropdowns();
        }
    }

    async function SaveStudent(event: CustomEvent) {
        await loadClasses(); 
    }

    onMount(() => {
        loadClasses();
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement;
            if (!target.closest('.more-container')) {
                closeAllDropdowns();
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    });
</script>

<div class="p-4 sm:p-[20px] bg-[#f8fafc] dark:bg-gray-950 h-screen transition-colors duration-200">
    
    <div class="flex justify-end items-center mb-6 sm:mb-[30px]">
        <button class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-none cursor-pointer font-semibold shadow-[0_4px_15px_rgba(102,126,234,0.3)] transition-all duration-300 hover:-translate-y-[2px] active:scale-95 flex items-center justify-center
            w-12 h-12 rounded-full text-2xl
            sm:w-auto sm:h-auto sm:py-[12px] sm:px-[28px] sm:rounded-[25px] sm:text-[14px]"
            on:click={toggleAddClassModal}>
            
            <span class="sm:hidden font-light">+</span> 
            <span class="hidden sm:inline">+ {$i18n.t('Add Class')}</span>
        </button>
        
        {#if showAddClassModal}
            <AddClassModal 
                selectedClassId={selectedClassId}
                className={selectedClassData?.name || ''}
                courseName={selectedClassData?.course || ''}
                on:close={() => {
                    showAddClassModal = false;
                    selectedClassId = null;
                    selectedClassData = null;
                }} 
                on:save={SaveClass} />
        {/if}
    </div>

    {#if loading}
        <div class="flex justify-center p-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
        </div>
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-4 sm:gap-[25px]">
            {#each classes as classe }
                <div class="bg-white dark:bg-gray-900 rounded-[16px] p-5 sm:p-[25px] shadow-[0_4px_12px_rgba(0,0,0,0.08)] border border-[#e2e8f0] dark:border-gray-800 transition-all duration-300 relative cursor-pointer hover:shadow-lg"
                on:click={() => goToClass(classe.id)}>
                    
                    <div class="flex gap-4 sm:gap-[18px] relative mb-4 sm:mb-[20px]">
                        <div class="w-[60px] h-[60px] sm:w-[70px] sm:h-[70px] bg-gradient-to-br from-[#eef2ff] to-[#e0e7ff] dark:from-gray-800 dark:to-gray-700 rounded-[12px] flex items-center justify-center flex-shrink-0">
                            <img src="/teacher/Classes.png" alt="Class_Icon" class="w-8 h-8 sm:w-[40px] sm:h-[40px] object-contain dark:brightness-110">
                        </div>
                        
                        <div class="flex-grow min-w-0">
                            <h3 class="m-0 mb-1 text-base sm:text-[18px] font-bold text-[#1e293b] dark:text-white truncate">
                                {classe.name}</h3>
                            <p class="m-0 text-[13px] sm:text-[14px] text-[#64748b] dark:text-gray-400 truncate">
                                <strong class="text-[#475569] dark:text-gray-300 font-semibold">{$i18n.t('Course')} :</strong> {classe.course}
                            </p>
                            <p class="m-0 mt-1 text-[13px] sm:text-[14px] text-[#64748b] dark:text-gray-400">
                                <strong class="text-[#475569] dark:text-gray-300 font-semibold">{$i18n.t('Total Students')} :</strong>
                                <span class="text-[#10b981] font-bold">{classe.student_count ?? 0}</span>
                            </p>
                        </div>

                        <div class="relative inline-block more-container">
                            <button 
                                class="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-gray-800 transition-all"
                                on:click|stopPropagation={() => toggleMoreDropdown(classe.id)}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
                            </button>

                            {#if showMoreDropdown === classe.id}
                                <div class="absolute right-0 mt-2 w-48 origin-top-right bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-slate-100 dark:border-gray-700 z-[100] overflow-hidden animate-in">
                                    <div class="py-1">
                                        <button class="w-full px-4 py-3 sm:py-2.5 flex items-center gap-3 text-sm text-slate-600 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-700 transition-colors"
                                            on:click|stopPropagation={() => ModifyClass(classe.id)}>
                                            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                                            <span>{$i18n.t('Update')}</span>
                                        </button>
                                        <button class="w-full px-4 py-3 sm:py-2.5 flex items-center gap-3 text-sm text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-colors"
                                            on:click|stopPropagation={() => DeleteClass(classe.id)}>
                                            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                                            <span>{$i18n.t('Delete')}</span>
                                        </button>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>

                    <button class="w-full p-[12px] bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-none rounded-[10px] cursor-pointer font-semibold text-[14px] transition-all duration-300 mt-2 active:scale-95" 
                    on:click|stopPropagation={() => openAddStudentModal(classe.id)}>
                        + {$i18n.t('Add Student')}
                    </button>
                </div>
            {:else}
                <div class="col-span-full text-center p-[60px_20px] bg-white dark:bg-gray-900 rounded-[16px] border-2 border-dashed border-[#e2e8f0] dark:border-gray-800">
                    <h3 class="text-[#475569] dark:text-gray-300 mb-[10px] text-[20px] font-bold">
                        {$i18n.t('No Classes Found')}
                    </h3>
                    <p class="text-[#94a3b8] dark:text-gray-500 mb-[25px]">
                        {$i18n.t('Start by creating your first class')}
                    </p>
                    <button class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-[12px] px-[28px] border-none rounded-[25px] cursor-pointer font-semibold transition-all hover:scale-105 active:scale-95"
                     on:click={toggleAddClassModal}>
                        + {$i18n.t('Create Class')}
                    </button>
                </div>
            {/each}
        </div>
    {/if}

    {#if showAddStudentModal}
        <AddStudentModal 
            classId={selectedClassId ||''} 
            on:close={() => (showAddStudentModal = false)}
            on:save={SaveStudent}
        />
    {/if}

    <ConfirmModal
        bind:open={showDeleteModal}
        title={$i18n.t('Delete Class')}
        message={$i18n.t('Are you sure you want to delete this class? This action cannot be undone.')}
        confirmText={$i18n.t('Delete')}
        cancelText={$i18n.t('Cancel')}
        onConfirm={confirmDelete}
    />
</div>

<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeIn 0.2s ease-out;
    }
</style>