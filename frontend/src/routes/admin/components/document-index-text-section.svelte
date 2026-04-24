<script lang="ts">
	import { documentsStore } from '$lib/hooks/store/use-documents.hook';
	import { toast } from 'svelte-sonner';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import ShTextarea from '$lib/components/sh-textarea/sh-textarea.svelte';
	import FileTextIcon from '@lucide/svelte/icons/file-text';

	let textTitle = $state('');
	let textContent = $state('');

	async function handleIndexText() {
		if (!textTitle.trim() || !textContent.trim()) {
			toast.error('Preencha o título e o conteúdo');
			return;
		}
		try {
			const result = await documentsStore.indexText(textTitle, textContent);
			toast.success(`Job ${result.job_id} criado`);
			textTitle = '';
			textContent = '';
		} catch (error) {
			toast.error(error instanceof Error ? error.message : 'Erro ao indexar');
		}
	}
</script>

<section class="rounded-xl border border-border bg-card p-4 shadow-sm">
	<h2 class="mb-3 font-semibold text-card-foreground">📝 Indexar texto puro</h2>
	<div class="flex flex-col gap-2">
		<ShInput bind:value={textTitle} placeholder="Título / nome do documento" />

		<ShTextarea bind:value={textContent} placeholder="Cole aqui o texto…" rows={4} />

		<ShButton onclick={handleIndexText} size="sm" class="gap-2 self-start">
			<FileTextIcon class="size-4" />
			Indexar texto
		</ShButton>
	</div>
</section>
