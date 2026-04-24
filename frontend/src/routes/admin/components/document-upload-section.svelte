<script lang="ts">
	import { documentsStore } from '$lib/hooks/store/use-documents.hook';
	import { toast } from 'svelte-sonner';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import UploadIcon from '@lucide/svelte/icons/upload';
	import ListIcon from '@lucide/svelte/icons/list';

	let { onShowSelected, onShowQueue } = $props<{
		onShowSelected: (files: File[]) => void;
		onShowQueue: () => void;
	}>();

	let uploadFiles = $state<File[]>([]);
	let uploadLoading = $state(false);
	let fileInputEl = $state<HTMLInputElement | null>(null);

	async function handleUpload() {
		if (uploadFiles.length === 0) return;
		uploadLoading = true;
		try {
			await documentsStore.uploadFiles(uploadFiles);
			toast.success('Arquivos enviados para indexação');
			uploadFiles = [];
			if (fileInputEl) fileInputEl.value = '';
			await documentsStore.fetchQueue();
		} catch (error) {
			toast.error(error instanceof Error ? error.message : 'Erro no upload');
		} finally {
			uploadLoading = false;
		}
	}
</script>

<section class="rounded-xl border border-border bg-card p-4 shadow-sm">
	<h2 class="mb-1 font-semibold text-card-foreground">📤 Upload de documentos</h2>
	<p class="mb-4 text-xs text-muted-foreground">PDF, Docx, TXT, Markdown — máximo 20 arquivos</p>

	<input
		bind:this={fileInputEl}
		type="file"
		accept=".pdf,.docx,.doc,.txt,.md"
		multiple
		class="hidden"
		onchange={(e) => {
			const files = (e.target as HTMLInputElement).files;
			uploadFiles = files ? Array.from(files) : [];
		}}
	/>

	<button
		type="button"
		onclick={() => fileInputEl?.click()}
		class="flex w-full cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed border-border px-4 py-6 transition-colors hover:border-primary hover:bg-primary/5"
	>
		<UploadIcon class="size-8 text-muted-foreground" />
		<span class="text-sm font-medium">Clique para selecionar arquivos</span>
		<span class="text-xs text-muted-foreground">ou arraste aqui</span>
	</button>

	{#if uploadFiles.length > 0}
		<div class="mt-3 flex items-center justify-between">
			<ShButton
				variant="outline"
				size="sm"
				class="gap-2"
				onclick={() => onShowSelected(uploadFiles)}
			>
				<ListIcon class="size-4" />
				Ver arquivos ({uploadFiles.length})
			</ShButton>

			<ShButton onclick={handleUpload} size="sm" class="gap-2" disabled={uploadLoading}>
				{#if uploadLoading}<ShSpinner class="size-4" />{:else}<UploadIcon class="size-4" />{/if}
				Enviar
			</ShButton>
		</div>
	{/if}

	{#if $documentsStore.jobs.length > 0}
		<div class="mt-4 flex items-center justify-between border-t pt-4">
			<p class="text-sm font-medium text-muted-foreground">
				{$documentsStore.jobs.length} em processamento
			</p>
			<ShButton variant="outline" size="sm" onclick={onShowQueue}>Ver fila</ShButton>
		</div>
	{/if}
</section>
