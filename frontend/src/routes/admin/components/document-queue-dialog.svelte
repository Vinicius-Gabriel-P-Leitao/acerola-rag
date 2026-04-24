<script lang="ts">
	import { documentsStore } from '$lib/hooks/store/use-documents.hook';
	import ShDialog from '$lib/components/sh-dialog/sh-dialog.svelte';
	import ShDialogContent from '$lib/components/sh-dialog/sh-dialog-content.svelte';
	import ShDialogHeader from '$lib/components/sh-dialog/sh-dialog-header.svelte';
	import ShDialogTitle from '$lib/components/sh-dialog/sh-dialog-title.svelte';
	import ShDialogFooter from '$lib/components/sh-dialog/sh-dialog-footer.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';

	let { open = $bindable() } = $props();

	const QUEUE_ICONS: Record<string, string> = {
		pending: '⏳',
		processing: '⚙️',
		done: '✅',
		error: '❌'
	};
</script>

<ShDialog bind:open>
	<ShDialogContent class="sm:max-w-2xl">
		<ShDialogHeader><ShDialogTitle>Fila de Processamento</ShDialogTitle></ShDialogHeader>
		<div class="flex max-h-[60vh] flex-col gap-3 overflow-y-auto">
			{#each $documentsStore.jobs as job (job.job_id)}
				<div class="border-b pb-2">
					<div class="flex justify-between text-sm font-medium">
						<span class="truncate">{job.filename}</span>
						<span>{QUEUE_ICONS[job.status] ?? '•'} {job.status}</span>
					</div>
					{#if job.error}<p class="mt-1 text-xs text-destructive">{job.error}</p>{/if}
				</div>
			{/each}
		</div>

		<ShDialogFooter>
			<ShButton variant="outline" onclick={() => (open = false)}>Fechar</ShButton>
		</ShDialogFooter>
	</ShDialogContent>
</ShDialog>
