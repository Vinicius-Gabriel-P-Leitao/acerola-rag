<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { mobileStore } from '$lib/hooks/ui/use-mobile.hook';
	import { themeStore } from '$lib/hooks/ui/use-theme.hook';
	import ShSonner from '$lib/components/sh-sonner/sh-sonner.svelte';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';
	import SettingsIcon from '@lucide/svelte/icons/settings';

	let { children } = $props();

	const navItems = [
		{ href: '/chat', label: 'Chat', Icon: MessageSquareIcon },
		{ href: '/admin', label: 'Admin', Icon: SettingsIcon }
	];

	onMount(() => {
		mobileStore.init();
		themeStore.init();
	});
</script>

<div class="flex h-screen overflow-hidden">
	<!-- Sidebar — desktop only -->
	<aside
		class="bg-sidebar border-sidebar-border hidden w-56 shrink-0 flex-col border-r md:flex"
		style="box-shadow: var(--shadow-sidebar);"
	>
		<div class="border-sidebar-border flex h-14 items-center border-b px-4">
			<span class="text-sidebar-foreground text-lg font-semibold">🍊 Acerola RAG</span>
		</div>
		<nav class="flex flex-col gap-1 p-2">
			{#each navItems as { href, label, Icon }}
				<a
					{href}
					class="text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors
						{page.url.pathname.startsWith(href) ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''}"
				>
					<Icon class="size-4" />
					{label}
				</a>
			{/each}
		</nav>
	</aside>

	<!-- Main content -->
	<main class="flex min-w-0 flex-1 flex-col overflow-hidden pb-14 md:pb-0">
		{@render children()}
	</main>
</div>

<!-- Bottom nav — mobile only -->
<nav
	class="border-border bg-background fixed bottom-0 left-0 right-0 flex border-t md:hidden"
	style="height:56px;"
>
	{#each navItems as { href, label, Icon }}
		<a
			{href}
			class="text-muted-foreground flex flex-1 flex-col items-center justify-center gap-1 text-xs transition-colors
				{page.url.pathname.startsWith(href) ? 'text-primary font-semibold' : ''}"
		>
			<Icon class="size-5" />
			{label}
		</a>
	{/each}
</nav>

<ShSonner />
