<script lang="ts">
import { onMount } from "svelte"

export let url: string
export let title: string = "PDF"
export let show: boolean = false
export let onClose: () => void

let isFullscreen = false

function toggleFullscreen(){
    const el = document.getElementById("pdf-modal")
    if(!document.fullscreenElement){
        el?.requestFullscreen()
    }else{
        document.exitFullscreen()
    }
}

onMount(()=>{
    const handleFsChange = () => {
        isFullscreen = !!document.fullscreenElement
    }
    document.addEventListener("fullscreenchange", handleFsChange)
    return () => document.removeEventListener("fullscreenchange", handleFsChange)
})
</script>

{#if show}
<div class="fixed inset-0 bg-gray-950/90 backdrop-blur-sm flex items-center justify-center z-50 transition-all">
    
    <div id="pdf-modal" class="bg-white dark:bg-gray-900 w-[95%] h-[95%] rounded-xl flex flex-col shadow-2xl overflow-hidden border dark:border-gray-800">
        
        {#if !isFullscreen}
            <div class="flex items-center justify-between px-5 py-3 border-b dark:border-gray-800 bg-gray-50 dark:bg-gray-950">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 rounded">
                        <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                    </div>
                    <span class="font-semibold text-gray-800 dark:text-gray-200 truncate max-w-[200px] sm:max-w-md">
                        {title}
                    </span>
                </div>

                <div class="flex items-center gap-2">
                    <button on:click={toggleFullscreen}
                        class="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 transition text-gray-600 dark:text-gray-400">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <polyline points="15 3 21 3 21 9"/>
                            <polyline points="9 21 3 21 3 15"/>
                            <line x1="21" y1="3" x2="14" y2="10"/>
                            <line x1="3" y1="21" x2="10" y2="14"/>
                        </svg>
                    </button>

                    <button on:click={onClose} 
                        class="p-2 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition text-red-500">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            </div>
        {/if}

        <div class="flex-1 w-full bg-white dark:bg-gray-900">
            <iframe 
                src={`/teacher/api/pdf/${url.split("/uploads/")[1]}`} 
                class="w-full h-full border-none" 
                title="PDF Viewer"
            />
        </div>
    </div>
</div>
{/if}