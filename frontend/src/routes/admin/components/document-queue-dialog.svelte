<script lang="ts">
	import { documentsStore } from '$lib/hooks/store/use-documents.hook';
	import ShResponsiveDialog from '$lib/components/sh-responsive-dialog/sh-responsive-dialog.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';

	let { open = $bindable() } = $props();

	const QUEUE_ICONS: Record<string, string> = {
		pending: '⏳',
		processing: '⚙️',
		done: '✅',
		error: '❌'
	};
</script>

<ShResponsiveDialog bind:open class="sm:max-w-2xl">
	{#snippet title()}
		Fila de Processamento
	{/snippet}

	{#snippet children()}
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
	{/snippet}

	{#snippet footer()}
		<ShButton variant="outline" onclick={() => (open = false)}>Fechar</ShButton>
	{/snippet}
</ShResponsiveDialog>
