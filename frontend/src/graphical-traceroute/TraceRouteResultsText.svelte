<script lang="ts">

  import DataTable, { Head, Body, Row, Cell as DataCell } from '@smui/data-table';
  import Paper, { Title, Content } from '@smui/paper';
  import LayoutGrid, { Cell as LayoutCell, InnerGrid } from '@smui/layout-grid';
  import Button, { Label } from '@smui/button';
  import Accordion, { Panel, Header, Content } from '@smui-extra/accordion';
  import axios from "axios";
  import {
    srcNode,
    destNode,
    numRoutes,
    searchDuration,
    tracerouteQueryResults,
    selectedDate
  } from '../store.js'


  function hopCompare( a, b ) {
    if ( a.ttl < b.ttl ){
      return -1;
    }
    if ( a.ttl > b.ttl ){
      return 1;
    }
    return 0;
  }

  $: console.dir($tracerouteQueryResults ? $tracerouteQueryResults[0].hops.sort( hopCompare ) : undefined)


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

      <Panel color="secondary" extend>

        <Header>
          Trace Route #{index + 1}
          <span slot="description">Trace route at: {traceroute.trace_time}</span>
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
