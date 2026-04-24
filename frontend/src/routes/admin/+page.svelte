<script lang="ts">
	import { onMount } from 'svelte';
	import { documentsStore, type DocumentMeta } from '$lib/hooks/store/use-documents.hook';
	import { useHeader } from '$lib/hooks/ui/use-header.svelte';
	import { toast } from 'svelte-sonner';

	// Componentes com caminhos corrigidos (kebab-case)
	import DocumentUploadSection from './components/document-upload-section.svelte';
	import DocumentIndexTextSection from './components/document-index-text-section.svelte';
	import DocumentListSection from './components/document-list-section.svelte';
	import DocumentViewerModal from './components/document-viewer-modal.svelte';
	import DocumentQueueDialog from './components/document-queue-dialog.svelte';

	import ShDialog from '$lib/components/sh-dialog/sh-dialog.svelte';
	import ShDialogContent from '$lib/components/sh-dialog/sh-dialog-content.svelte';
	import ShDialogHeader from '$lib/components/sh-dialog/sh-dialog-header.svelte';
	import ShDialogTitle from '$lib/components/sh-dialog/sh-dialog-title.svelte';
	import ShDialogDescription from '$lib/components/sh-dialog/sh-dialog-description.svelte';
	import ShDialogFooter from '$lib/components/sh-dialog/sh-dialog-footer.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';

	let viewOpen = $state(false);
	let viewLoading = $state(false);
	let viewDoc = $state<{ source: string; content: string } | null>(null);

	let queueOpen = $state(false);
	let deleteOpen = $state(false);
	let deleteDoc = $state<DocumentMeta | null>(null);
	let deleteLoading = $state(false);

	const headerStore = useHeader();
	headerStore.title = 'Admin';

	onMount(() => {
		documentsStore.fetchPage();
		documentsStore.fetchQueue();
		const interval = setInterval(documentsStore.fetchQueue, 3000);
		return () => clearInterval(interval);
	});

	async function openViewer(source: string) {
		viewLoading = true;
		viewOpen = true;
		try {
			const content = await documentsStore.getContent(source);
			viewDoc = { source, content };
		} catch {
			toast.error('Erro ao carregar');
			viewOpen = false;
		} finally {
			viewLoading = false;
		}
	}

	async function confirmDelete() {
		if (!deleteDoc) return;
		deleteLoading = true;
		try {
			const count = await documentsStore.deleteDocument(deleteDoc.source);
			toast.success(`${count} chunks removidos`);
			deleteOpen = false;
			deleteDoc = null;
		} catch {
			toast.error('Erro ao deletar');
		} finally {
			deleteLoading = false;
		}
	}
</script>

<div class="flex flex-1 flex-col overflow-y-auto p-4">
	<div class="mx-auto flex w-full max-w-full flex-col gap-6 md:max-w-[60%]">
		<DocumentUploadSection
			onShowSelected={(_files: File[]) => {
				/* implemente se quiser abrir o modal de lista */
			}}
			onShowQueue={() => (queueOpen = true)}
		/>

		<DocumentIndexTextSection />

		<DocumentListSection
			onView={openViewer}
			onDelete={(doc: DocumentMeta) => {
				deleteDoc = doc;
				deleteOpen = true;
			}}
		/>
	</div>
</div>

<DocumentViewerModal bind:open={viewOpen} doc={viewDoc} loading={viewLoading} />
<DocumentQueueDialog bind:open={queueOpen} />

<ShDialog bind:open={deleteOpen}>
	<ShDialogContent>
		<ShDialogHeader>
			<ShDialogTitle>Confirmar exclusão</ShDialogTitle>

			<ShDialogDescription>
				Deletar <strong>{deleteDoc?.source}</strong>? Esta ação é irreversível.
			</ShDialogDescription>
		</ShDialogHeader>

		<ShDialogFooter>
			<ShButton variant="outline" onclick={() => (deleteOpen = false)}>Cancelar</ShButton>
			<ShButton variant="destructive" disabled={deleteLoading} onclick={confirmDelete}>
				{#if deleteLoading}<ShSpinner class="mr-2 size-4" />{/if}
				Confirmar
			</ShButton>
		</ShDialogFooter>
	</ShDialogContent>
</ShDialog>
