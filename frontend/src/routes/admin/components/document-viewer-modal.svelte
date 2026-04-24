<script lang="ts">
	import ShResponsiveDialog from '$lib/components/sh-responsive-dialog/sh-responsive-dialog.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';

	let {
		open = $bindable(),
		doc,
		loading
	} = $props<{
		open: boolean;
		doc: { source: string; content: string } | null;
		loading: boolean;
	}>();
</script>

<ShResponsiveDialog
	bind:open
	class="w-[95vw] sm:max-w-300"
	contentClass="flex min-h-0 flex-1 flex-col"
>
	{#snippet title()}
		{doc?.source ?? 'Carregando...'}
	{/snippet}

	{#if loading}
		<div class="flex flex-1 items-center justify-center py-10">
			<ShSpinner class="size-6" />
		</div>
	{:else if doc}
		<textarea
			readonly
			class="h-[55vh] w-full resize-none rounded-md border bg-muted p-3 font-mono text-xs focus:outline-none md:h-[60vh] md:text-sm"
			value={doc.content}
		></textarea>
	{/if}
</ShResponsiveDialog>
