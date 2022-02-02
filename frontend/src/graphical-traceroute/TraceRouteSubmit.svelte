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
    selectedDate,
    backendBaseURL
  } from '../store.js'

  // export let backendBaseURL;


  export let traceroutes = [];

  $: console.dir(traceroutes);

  async function submitQuery() {

    let params = {
      src: $srcNode,
      dest: $destNode,
      search_duration: $searchDuration,
      start_dt: $selectedDate,
      num_tracert: $numRoutes
    };

    traceroutes = await axios.get($backendBaseURL + '/traceroute', { params: params }).then((x) => x.data);
  };

</script>


<Paper color="primary" variant="outlined" class="mdc-theme--primary">
  <Title>Chosen Trace Route Query Parameters</Title>
  <Content>
    <LayoutGrid>

      <!-- ROW -->
      <LayoutCell span="1">
      </LayoutCell>

      <LayoutCell span="8">

        <DataTable table$aria-label="Traceroute query list" style="max-width: 100%;">
          <Head>
            <Row>
              <DataCell numeric>Number of Traceroutes</DataCell>
              <DataCell>Source Node</DataCell>
              <DataCell>Destination Node</DataCell>
              <DataCell>Search Duration</DataCell>
              <DataCell>Start Date</DataCell>
            </Row>
          </Head>
          <Body>
            <Row>
              <DataCell>
                {$numRoutes}
              </DataCell>
              <DataCell>
                {$srcNode}
              </DataCell>
              <DataCell>
                {$destNode}
              </DataCell>
              <DataCell>
                {$searchDuration}
              </DataCell>
              <DataCell>
                {$selectedDate}
              </DataCell>

            </Row>
          </Body>
        </DataTable>

      </LayoutCell>

      <LayoutCell span="3">
        <Button variant="raised"
            on:click={submitQuery}
          >
          <!-- <Icon class="material-icons">refresh</Icon> -->
          <Label>Submit Query</Label>
        </Button>
      </LayoutCell>
  </LayoutGrid>
  </Content>
</Paper>
