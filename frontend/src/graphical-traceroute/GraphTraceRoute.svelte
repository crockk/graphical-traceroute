<script>

  import QueryInput from './QueryInput.svelte'
  let srcNode;
  let destNode;
  let numRoutes;

</script>

<QueryInput
  bind:srcNode={srcNode}
  bind:destNode={destNode}
  bind:numRoutes={numRoutes}
/>



{srcNode}
{destNode}
{numRoutes}
