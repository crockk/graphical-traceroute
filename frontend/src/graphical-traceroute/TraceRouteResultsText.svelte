<script lang="ts">

  import DataTable, { Head, Body, Row, Cell as DataCell } from '@smui/data-table';
  import Paper, { Title, Content } from '@smui/paper';
  import LayoutGrid, { Cell as LayoutCell, InnerGrid } from '@smui/layout-grid';
  import Button, { Label } from '@smui/button';
  import Accordion, { Panel, Header, Content } from '@smui-extra/accordion';
  import IconButton, { Icon } from '@smui/icon-button';
  import axios from "axios";
  import {
    backendBaseURL,
    tracerouteQueryResults,
    maxRoutes
  } from '../store.js'
  import { onMount } from 'svelte';

  function hopCompare( a, b ) {
    if ( a.ttl < b.ttl ){
      return -1;
    }
    if ( a.ttl > b.ttl ){
      return 1;
    }
    return 0;
  }

  async function getMaxRoutes() {
    $maxRoutes = await axios.get($backendBaseURL + '/max-routes').then((x) => x.data.max_routes);
  };

  function updatePanelOpenList(index){
    panelOpenList[index] = !panelOpenList[index];
  }

  $: console.dir($tracerouteQueryResults ? $tracerouteQueryResults[0].hops.sort( hopCompare ) : undefined)

  $: panelOpenList = new Array($maxRoutes).fill(false);

  onMount(() => {
    getMaxRoutes();
	});
</script>

{#if (! $tracerouteQueryResults)}
  <LayoutGrid>

    <!-- ROW -->
    <LayoutCell span="1">
    </LayoutCell>

    <LayoutCell span="4">
      No traceroutes found
    </LayoutCell>

    <LayoutCell span="7">
    </LayoutCell>
  </LayoutGrid>
{/if}

<Accordion multiple>

  {#if ($tracerouteQueryResults)}
    {#each $tracerouteQueryResults as traceroute, index}

      <Panel color="secondary" on:click="{ () => {updatePanelOpenList(index)} }" extend>

        <Header>
          Trace Route #{index + 1}
          <span slot="description">Trace route at: {traceroute.trace_time}</span>
          <IconButton slot="icon" toggle pressed={panelOpenList[index]}>
            <Icon class="material-icons" on>expand_less</Icon>
            <Icon class="material-icons">expand_more</Icon>
          </IconButton>
        </Header>

        <Content>

          <DataTable stickyHeader table$aria-label="Traceroute hop list" style="max-width: 100%;">

            <Head>

              <Row>
                <DataCell numeric>Time To Live (ttl)</DataCell>
                <DataCell>Host</DataCell>
              </Row>

            </Head>

            <Body>

              {#each traceroute.hops.sort( hopCompare ) as hop}

                <Row>

                  <DataCell>
                    {hop.ttl}
                  </DataCell>
                  <DataCell>
                    {hop.host}
                  </DataCell>

                </Row>

              {/each}

            </Body>

          </DataTable>

        </Content>

      </Panel>

    {/each}
  {/if}

</Accordion>
