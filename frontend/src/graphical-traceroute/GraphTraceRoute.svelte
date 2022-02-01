<script>

  import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';
  import TraceRouteParams from './TraceRouteParams.svelte'
  import Paper, { Title, Content } from '@smui/paper';

  let srcNode;
  let destNode;
  let numRoutes;
  let searchDuration;
  let selectedDate;

</script>

<TraceRouteParams
  bind:srcNode={srcNode}
  bind:destNode={destNode}
  bind:numRoutes={numRoutes}
  bind:searchDuration={searchDuration}
  bind:selectedDate={selectedDate}
/>

<br>

<Paper color="primary" variant="outlined" class="mdc-theme--primary">
  <Title>Chosen Trace Route Query Parameters</Title>
  <Content>

    <DataTable table$aria-label="Traceroute query list" style="max-width: 100%;">
      <Head>
        <Row>
          <Cell numeric>Number of Traceroutes</Cell>
          <Cell>Source Node</Cell>
          <Cell>Destination Node</Cell>
          <Cell>Search Duration</Cell>
          <Cell>Start Date</Cell>
        </Row>
      </Head>
      <Body>
        <Row>
          <Cell>
            {numRoutes}
          </Cell>
          <Cell>
            {srcNode}
          </Cell>
          <Cell>
            {destNode}
          </Cell>
          <Cell>
            {searchDuration}
          </Cell>
          <Cell>
            {selectedDate}
          </Cell>

        </Row>
      </Body>
    </DataTable>

  </Content>
</Paper>
