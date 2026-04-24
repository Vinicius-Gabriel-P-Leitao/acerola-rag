<script lang="ts">
	import ShDrawer from './sh-drawer.svelte';
	import ShDrawerContent from './sh-drawer-content.svelte';
	import ShDrawerDescription from './sh-drawer-description.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof ShDrawerDescription> = $props();
</script>

<ShDrawer open={true}>
	<ShDrawerContent>
		<ShDrawerDescription {...restProps} />
	</ShDrawerContent>
</ShDrawer>
