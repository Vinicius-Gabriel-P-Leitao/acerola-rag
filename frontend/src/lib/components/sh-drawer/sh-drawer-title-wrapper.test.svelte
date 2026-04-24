<script lang="ts">
	import ShDrawer from './sh-drawer.svelte';
	import ShDrawerContent from './sh-drawer-content.svelte';
	import ShDrawerTitle from './sh-drawer-title.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof ShDrawerTitle> = $props();
</script>

<ShDrawer open={true}>
	<ShDrawerContent>
		<ShDrawerTitle {...restProps} />
	</ShDrawerContent>
</ShDrawer>
