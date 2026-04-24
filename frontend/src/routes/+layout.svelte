<script lang="ts">
	import './layout.css';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { mobileStore } from '$lib/hooks/ui/use-mobile.hook';
	import { themeStore } from '$lib/hooks/ui/use-theme.hook';
	import { initHeader } from '$lib/hooks/ui/use-header.svelte';
	import { historyStore } from '$lib/hooks/store/use-history.hook';
	import { chatStore } from '$lib/hooks/store/use-chat.hook';
	import faviconPng from '$lib/assets/favicon.png';
	import ShSonner from '$lib/components/sh-sonner/sh-sonner.svelte';
	import ShThemeToggle from '$lib/components/sh-theme-toggle/sh-theme-toggle.svelte';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';
	import HistoryIcon from '@lucide/svelte/icons/history';
	import SettingsIcon from '@lucide/svelte/icons/settings';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import PanelLeftIcon from '@lucide/svelte/icons/panel-left';
	import TrashIcon from '@lucide/svelte/icons/trash-2';

	let { children } = $props();

	const headerStore = initHeader();

	let sidebarOpen = $state(true);
	let searchInput = $state('');
	let searchDebounce: ReturnType<typeof setTimeout>;

	const navItems = [
		{ href: '/chat', label: 'Chat', Icon: MessageSquareIcon },
		{ href: '/history', label: 'Histórico', Icon: HistoryIcon },
		{ href: '/admin', label: 'Admin', Icon: SettingsIcon }
	];

	onMount(() => {
		mobileStore.init();
		themeStore.init();
		historyStore.load();
	});

	function newConversation() {
		chatStore.clear();
		goto('/chat');
	}

	function openConversation(id: string) {
		chatStore.loadConversation(id);
		goto('/chat');
	}

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => historyStore.search(searchInput), 300);
	}

	async function removeConversation(e: MouseEvent, id: string) {
		e.stopPropagation();
		await historyStore.remove(id);
		if (chatStore.conversationId === id) {
			chatStore.clear();
		}
	}

	function formatRelative(iso: string) {
		const d = new Date(iso);
		const now = new Date();
		const diff = (now.getTime() - d.getTime()) / 1000;
		if (diff < 60) return 'agora';
		if (diff < 3600) return `${Math.floor(diff / 60)}min`;
		if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
		return `${Math.floor(diff / 86400)}d`;
	}
</script>

<div class="flex h-[100dvh] overflow-hidden">
	<!-- Sidebar — desktop only -->
	<aside
		class="hidden shrink-0 flex-col border-r border-sidebar-border bg-sidebar transition-all duration-200 md:flex
			{sidebarOpen ? 'w-56' : 'w-14'}"
		style="box-shadow: var(--shadow-sidebar);"
	>
		<!-- Logo + toggle -->
		<div class="flex h-14 items-center gap-2 border-b border-sidebar-border px-3">
			{#if sidebarOpen}
				<img src={faviconPng} alt="Acerola RAG" class="h-6 w-6 shrink-0" />
				<span class="flex-1 truncate text-base font-semibold text-sidebar-foreground"
					>Acerola RAG</span
				>
			{/if}
			<button
				class="ml-auto flex size-7 items-center justify-center rounded-md text-sidebar-foreground opacity-60 hover:bg-sidebar-accent hover:opacity-100"
				onclick={() => (sidebarOpen = !sidebarOpen)}
				title="Alternar sidebar"
			>
				<PanelLeftIcon class="size-4" />
			</button>
		</div>

		<!-- Nova conversa -->
		<div class="px-2 pt-2">
			<button
				onclick={newConversation}
				class="flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
			>
				<PlusIcon class="size-4 shrink-0" />
				{#if sidebarOpen}<span>Nova conversa</span>{/if}
			</button>
		</div>

		<!-- Nav items -->
		<nav class="flex flex-col gap-0.5 px-2 pt-1">
			{#each navItems as { href, label, Icon } (href)}
				<a
					{href}
					class="flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground
						{page.url.pathname.startsWith(href) ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''}"
					title={sidebarOpen ? undefined : label}
				>
					<Icon class="size-4 shrink-0" />
					{#if sidebarOpen}<span>{label}</span>{/if}
				</a>
			{/each}
		</nav>

		<!-- History list -->
		{#if sidebarOpen}
			<div class="mt-3 min-h-0 flex-1 overflow-hidden px-2">
				<p
					class="mb-1 px-1 text-[10px] font-semibold tracking-wider text-muted-foreground uppercase"
				>
					Últimas conversas
				</p>

				<!-- Search -->
				<input
					type="text"
					bind:value={searchInput}
					oninput={onSearchInput}
					placeholder="Buscar…"
					class="mb-1.5 w-full rounded-md border border-border bg-background px-2 py-1 text-xs text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-ring focus:outline-none"
				/>

				<div class="flex flex-col gap-0.5 overflow-y-auto" style="max-height: calc(100dvh - 260px)">
					{#if $historyStore.conversations.length === 0}
						<p class="px-1 text-xs text-muted-foreground">Nenhuma conversa ainda.</p>
					{/if}
					{#each $historyStore.conversations as conv (conv.id)}
						<div
							role="button"
							tabindex="0"
							onclick={() => openConversation(conv.id)}
							onkeydown={(e) => e.key === 'Enter' && openConversation(conv.id)}
							class="group flex w-full cursor-pointer items-center gap-1.5 rounded-md px-2 py-1.5 text-left transition-colors hover:bg-sidebar-accent
								{$chatStore.conversationId === conv.id ? 'bg-sidebar-accent' : ''}"
						>
							<span class="min-w-0 flex-1 truncate text-xs text-sidebar-foreground"
								>{conv.title}</span
							>
							<span class="shrink-0 text-[10px] text-muted-foreground"
								>{formatRelative(conv.updated_at)}</span
							>
							<button
								class="hidden size-4 shrink-0 items-center justify-center text-muted-foreground group-hover:flex hover:text-destructive"
								onclick={(e) => removeConversation(e, conv.id)}
								title="Apagar conversa"
							>
								<TrashIcon class="size-3" />
							</button>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</aside>

	<!-- Main content -->
	<div class="flex min-w-0 flex-1 flex-col overflow-hidden">
		<!-- Global Header -->
		<header
			class="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background px-4"
			style="box-shadow: var(--shadow-header);"
		>
			<span class="font-semibold">{headerStore.title}</span>

			<div class="flex items-center gap-2">
				{#if headerStore.action}
					{@render headerStore.action()}
				{/if}
				<ShThemeToggle />
			</div>
		</header>

		<main class="flex min-w-0 flex-1 flex-col overflow-hidden pb-[56px] md:pb-0">
			{@render children()}
		</main>
	</div>
</div>

<!-- Bottom nav — mobile only -->
<nav
	class="fixed right-0 bottom-0 left-0 flex border-t border-border bg-background md:hidden"
	style="height:56px;"
>
	{#each navItems as { href, label, Icon } (href)}
		<a
			{href}
			class="flex flex-1 flex-col items-center justify-center gap-1 text-xs text-muted-foreground transition-colors
				{page.url.pathname.startsWith(href) ? 'font-semibold text-primary' : ''}"
		>
			<Icon class="size-5" />
			{label}
		</a>
	{/each}
</nav>

<ShSonner />
