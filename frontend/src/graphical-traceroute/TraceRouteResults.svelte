<script lang="ts">

  import DataTable, { Head, Body, Row, Cell as DataCell } from '@smui/data-table';
  import Paper, { Title, Content } from '@smui/paper';
  import LayoutGrid, { Cell as LayoutCell, InnerGrid } from '@smui/layout-grid';
  import Button, { Label } from '@smui/button';
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



<Paper color="primary" variant="outlined" class="mdc-theme--primary">
  <Title>Trace Route Results</Title>
  <Content>
    <LayoutGrid>

      <!-- ROW -->
      <LayoutCell span="1">
      </LayoutCell>

      <LayoutCell span="4">
      {$tracerouteQueryResults ? "" : 'No traceroutes found' }
      <!-- {$tracerouteQueryResults ? JSON.stringify($tracerouteQueryResults[0].hops.sort( hopCompare )) : 'No traceroutes found' } -->
      </LayoutCell>

      <LayoutCell span="7">
      </LayoutCell>

      <!-- ROW -->

      {#if ($tracerouteQueryResults)}
        {#each $tracerouteQueryResults as traceroute}
          <LayoutCell span="12">
            <InnerGrid>

              <LayoutCell span="1">
              </LayoutCell>

              <LayoutCell span="2">
                Time recorded: {traceroute.trace_time}
              </LayoutCell>

              <LayoutCell span="1">
              </LayoutCell>

              <LayoutCell span="8">

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

              </LayoutCell>

            </InnerGrid>
          </LayoutCell>
        {/each}
      {/if}

    </LayoutGrid>
  </Content>
</Paper>
