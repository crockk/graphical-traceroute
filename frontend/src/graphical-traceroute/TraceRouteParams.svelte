<script>
  import Button from '@smui/button';
  import { Label, Icon as CommonIcon } from '@smui/common';
  import Select, { Option } from '@smui/select';
  import Slider from '@smui/slider';
  import FormField from '@smui/form-field';
  import Icon from '@smui/select/icon';
  import LayoutGrid, { Cell, InnerGrid } from '@smui/layout-grid';
  import Textfield from '@smui/textfield';
  import Paper, { Title, Content } from '@smui/paper';
  import DatePicker from "@beyonk/svelte-datepicker/src/components/DatePicker.svelte";
  import axios from "axios";
  import {
    srcNode,
    destNode,
    numRoutes,
    searchDuration,
    selectedDate,
    backendBaseURL
  } from '../store.js'
	import { onMount } from 'svelte';

  // const backendBaseURL = "http://localhost:8100"
  // export let backendBaseURL;

  let promiseMaxRoutes;
  let promiseSrcNodes;
  let promiseDestNodes;

  function getMaxRoutes() {
    promiseMaxRoutes = axios.get($backendBaseURL + '/max-routes').then((x) => x.data);
  };

  function getSrcNodes() {
    promiseSrcNodes = axios.get($backendBaseURL + '/src').then((x) => x.data);
  };

  function getDestNodes() {
    promiseDestNodes = axios.get($backendBaseURL + '/dest').then((x) => x.data);
  };

  getMaxRoutes();
  getSrcNodes();
  getDestNodes();

  let searchDurationTypes = [
    {
      typeName: "seconds",
      symbol:"s"
    },
    {
      typeName: "minutes",
      symbol:"m"
    },
    {
      typeName: "hours",
      symbol:"h"
    },
    {
      typeName: "days",
      symbol:"d"
    }
  ];
  let searchDurationType = searchDurationTypes[2].symbol;

  let searchDurationLength = 6;

  $: $searchDuration = searchDurationLength + searchDurationType

	let selectedDateRaw;
  let dateTimeFormat = "YYYY-MM-DD HH:mm:ss";

  $: $selectedDate = selectedDateRaw ? formateDateString(selectedDateRaw) : undefined;

  function formateDateString(dateObj) {
    if(dateObj){
      dateObj.setMinutes( dateObj.getMinutes() - dateObj.getTimezoneOffset() );
      return dateObj.toISOString().replace("T"," ").split(".")[0];
    } else {
      return undefined;
    };
  };

  onMount(() => {
    // Manually add min and max attributes to search duration length input field
    let searchDurationFieldID = "searchDurationField"
    let searchDurationField = document.getElementById(searchDurationFieldID);
    let searchDurationInputField = searchDurationField.getElementsByTagName("input")[0];
    searchDurationInputField.setAttribute("max",1000)
    searchDurationInputField.setAttribute("min",1)
	});

</script>

<Paper color="primary" variant="outlined" class="mdc-theme--primary">
  <Title>
    <LayoutGrid>
      <Cell span="9">
        Select Trace Route Query Parameters

      </Cell>

      <Cell span="3">
        <Button variant="raised"
            on:click={getMaxRoutes}
            on:click={getSrcNodes}
            on:click={getDestNodes}
          >
          <CommonIcon class="material-icons">refresh</CommonIcon>
          <Label>Route Parameters</Label>
        </Button>
      </Cell>
    </LayoutGrid>

  </Title>
  <Content>

    <LayoutGrid>

      <!-- ROW -->
      <Cell span="1">
      </Cell>

      <Cell span="3">

        <Select
          class="shaped-outlined"
          variant="outlined"
          bind:value={$srcNode}
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
          bind:value={$destNode}
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

      <Cell span="2">
        <Textfield
          id="searchDurationField"
          variant="filled"
          bind:value={searchDurationLength}
          label="Search Duration"
          type="number"
          suffix="{ searchDurationType }"
          required
        />
      </Cell>

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
            <Option value={durationTypes.symbol}>{durationTypes.typeName}</Option>
          {/each}

        </Select>
      </Cell>

      <Cell span="3">
        <DatePicker
          time={true}
          bind:selected={ selectedDateRaw }
          format={ dateTimeFormat }
        >
        </DatePicker>
      </Cell>

      <Cell span="2">
      </Cell>

      <!-- ROW -->
      <Cell span="1">
      </Cell>

      <Cell span="6">
        {#await promiseMaxRoutes then maxRoutes}
          {#if maxRoutes}
            <Slider
              bind:value={$numRoutes}
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

        <Button variant="raised" color="secondary" ripple={false}>
          <Label>Max Routes: { $numRoutes }</Label>
        </Button>

      </Cell>

      <Cell span="3">
      </Cell>

    </LayoutGrid>
  </Content>
</Paper>
