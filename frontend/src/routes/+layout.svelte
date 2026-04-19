<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { mobileStore } from '$lib/hooks/ui/use-mobile.hook';
	import { themeStore } from '$lib/hooks/ui/use-theme.hook';
	import { initHeader } from '$lib/hooks/ui/use-header.svelte';
	import ShSonner from '$lib/components/sh-sonner/sh-sonner.svelte';
	import ShThemeToggle from '$lib/components/sh-theme-toggle/sh-theme-toggle.svelte';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';
	import SettingsIcon from '@lucide/svelte/icons/settings';

	let { children } = $props();

	const headerStore = initHeader();

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
		class="hidden w-56 shrink-0 flex-col border-r border-sidebar-border bg-sidebar md:flex"
		style="box-shadow: var(--shadow-sidebar);"
	>
		<div class="flex h-14 items-center justify-center border-b border-sidebar-border px-4">
			<span class="text-lg font-semibold text-sidebar-foreground">🍊 Acerola RAG</span>
		</div>
		<nav class="flex flex-col gap-1 p-2">
			{#each navItems as { href, label, Icon } (href)}
				<a
					{href}
					class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground
						{page.url.pathname.startsWith(href) ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''}"
				>
					<Icon class="size-4" />
					{label}
				</a>
			{/each}
		</nav>
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

		<main class="flex min-w-0 flex-1 flex-col overflow-hidden pb-14 md:pb-0">
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
