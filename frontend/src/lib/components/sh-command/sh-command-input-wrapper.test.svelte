<script lang="ts">
	import ShCommand from './sh-command.svelte';
	import ShCommandInput from './sh-command-input.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof ShCommandInput> = $props();
</script>

<ShCommand>
	<ShCommandInput {...restProps} />
</ShCommand>
