<script>
  import Button from '@smui/button';
  import { Label } from '@smui/common';
  import Select, { Option } from '@smui/select';
  import Slider from '@smui/slider';
  import FormField from '@smui/form-field';
  import Icon from '@smui/select/icon';
  import LayoutGrid, { Cell, InnerGrid } from '@smui/layout-grid';

  const backendBaseURL = "http://localhost:8100"

  let promiseMaxRoutes;
  let promiseSrcNodes;
  let promiseDestNodes;

  function getMaxRoutes() {
    promiseMaxRoutes = fetch(backendBaseURL + '/max-routes', {
      mode: 'cors',
    }).then((x) => x.json());
  };

  function getSrcNodes() {
    promiseSrcNodes = fetch(backendBaseURL + '/src', {
      mode: 'cors',
    }).then((x) => x.json());
  };

  function getDestNodes() {
    promiseDestNodes = fetch(backendBaseURL + '/dest', {
      mode: 'cors',
    }).then((x) => x.json());
  };

  export let srcNode;
  export let destNode;
  export let numRoutes = 1;

  getMaxRoutes();
  getSrcNodes();
  getDestNodes();

  let searchDurationTypes = ["s", "m", "h", "d"];
  let searchDurationType = searchDurationTypes[2];

</script>

<LayoutGrid>

  <!-- ROW -->
  <Cell span="1">
  </Cell>

  <Cell span="8">
    {#await promiseMaxRoutes then maxRoutes}
      {#if maxRoutes}
        <Slider
          bind:value={numRoutes}
          min={1}
          max={ maxRoutes.max_routes }
          discrete
          tickMarks
          input$aria-label="Tick mark slider for max trace routes"
        />
      {/if}
    {/await}
  </Cell>

  <Cell span="2">

    <Button variant="raised" disabled>
      <Label>Max Routes: { numRoutes }</Label>
    </Button>

  </Cell>

  <Cell span="1">
  </Cell>

  <!-- ROW -->
  <Cell span="1">
  </Cell>

  <Cell span="3">

    <Select
      class="shaped-outlined"
      variant="outlined"
      bind:value={srcNode}
      label="Source Node"
      required
    >
      <Icon class="material-icons" slot="leadingIcon">computer</Icon>
      <!-- <Option value="" /> -->

      {#await promiseSrcNodes then srcNodes}
        {#if srcNodes}
          {#each srcNodes as sNode}
            <Option value={sNode}>{sNode}</Option>
          {/each}
        {/if}
      {/await}
    </Select>

  </Cell>

  <Cell span="3">

    <Select
      class="shaped-outlined"
      variant="outlined"
      bind:value={destNode}
      label="Destination Node"
      required
    >
      <Icon class="material-icons" slot="leadingIcon">dns</Icon>
      <!-- <Option value="" /> -->

      {#await promiseDestNodes then destNodes}
        {#if destNodes}
          {#each destNodes as dNode}
            <Option value={dNode}>{dNode}</Option>
          {/each}
        {/if}
      {/await}
    </Select>

  </Cell>

  <Cell span="5">
  </Cell>

  <!-- ROW -->
  <Cell span="1">
  </Cell>

  <Cell span="3">
    <Select
      class="shaped-outlined"
      variant="outlined"
      bind:value={searchDurationType}
      label="Search Duration Type"
      required
    >
      <Icon class="material-icons" slot="leadingIcon">schedule</Icon>
      <!-- <Option value="" /> -->

      {#each searchDurationTypes as durationTypes}
        <Option value={durationTypes}>{durationTypes}</Option>
      {/each}

    </Select>
  </Cell>

  <Cell span="8">
  </Cell>

  <!-- ROW -->
  <Cell span="9">
  </Cell>

  <Cell span="3">
    <Button variant="raised"
        on:click={getMaxRoutes}
        on:click={getSrcNodes}
        on:click={getDestNodes}
      >
      <Icon class="material-icons">refresh</Icon>
      <Label>Route Parameters</Label>
    </Button>
  </Cell>

</LayoutGrid>
