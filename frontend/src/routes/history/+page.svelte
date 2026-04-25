<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { historyStore } from '$lib/hooks/store/use-history.hook';
	import { chatStore } from '$lib/hooks/store/use-chat.hook';
	import { useHeader } from '$lib/hooks/ui/use-header.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShSkeleton from '$lib/components/sh-skeleton/sh-skeleton.svelte';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import TrashIcon from '@lucide/svelte/icons/trash-2';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';

	const headerStore = useHeader();
	headerStore.title = 'Histórico';

	let searchInput = $state('');
	let searchDebounce: ReturnType<typeof setTimeout>;
	let deleteLoading = $state<string | null>(null);

	onMount(() => {
		historyStore.load();
	});

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => historyStore.search(searchInput), 300);
	}

	function openConversation(id: string) {
		chatStore.loadConversation(id);
		goto('/chat');
	}

	async function removeConversation(id: string) {
		deleteLoading = id;
		try {
			await historyStore.remove(id);
			if (chatStore.conversationId === id) chatStore.clear();
			toast.success('Conversa apagada');
		} catch {
			toast.error('Erro ao apagar conversa');
		} finally {
			deleteLoading = null;
		}
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleString('pt-BR', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="flex flex-1 flex-col overflow-y-auto">
	<div class="mx-auto flex w-full max-w-2xl min-w-0 flex-col gap-4 p-4">
		<div class="flex items-center gap-3">
			<ShInput
				class="flex-1"
				placeholder="🔍 Buscar em conversas…"
				bind:value={searchInput}
				oninput={onSearchInput}
			/>
		</div>

		{#if $historyStore.loading}
			<div class="flex flex-col gap-3">
				{#each { length: 5 } as _, i (i)}
					<ShSkeleton class="h-16 w-full rounded-xl" />
				{/each}
			</div>
		{:else if $historyStore.conversations.length === 0}
			<div class="flex flex-col items-center gap-2 py-20 text-muted-foreground">
				<MessageSquareIcon class="size-10 opacity-30" />
				<p class="text-sm">
					{searchInput ? 'Nenhum resultado encontrado.' : 'Nenhuma conversa ainda.'}
				</p>
			</div>
		{:else}
			<div class="flex flex-col gap-2">
				{#each $historyStore.conversations as conv (conv.id)}
					<div
						class="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:bg-accent/40"
					>
						<button class="min-w-0 flex-1 text-left" onclick={() => openConversation(conv.id)}>
							<p class="truncate text-sm font-medium text-foreground">{conv.title}</p>
							<p class="mt-0.5 text-xs text-muted-foreground">{formatDate(conv.updated_at)}</p>
						</button>
						<ShButton
							variant="ghost"
							size="icon-sm"
							class="shrink-0 text-muted-foreground hover:text-destructive"
							disabled={deleteLoading === conv.id}
							onclick={() => removeConversation(conv.id)}
							title="Apagar conversa"
						>
							<TrashIcon class="size-4" />
						</ShButton>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
