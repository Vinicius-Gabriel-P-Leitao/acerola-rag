<script lang="ts">
	import { themeStore } from '$lib/hooks/ui/use-theme.hook';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import SunIcon from '@lucide/svelte/icons/sun';
	import MoonIcon from '@lucide/svelte/icons/moon';

	let { class: className }: { class?: string } = $props();
</script>

<ShButton
	variant="ghost"
	size="icon"
	class={className}
	onclick={() => themeStore.toggle()}
	title={$themeStore === 'dark' ? 'Mudar para claro' : 'Mudar para escuro'}
>
	{#if $themeStore === 'dark'}
		<SunIcon class="size-4" />
	{:else}
		<MoonIcon class="size-4" />
	{/if}
</ShButton>
