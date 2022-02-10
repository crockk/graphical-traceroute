import { writable, readable } from 'svelte/store'

const srcNode = writable(undefined);
const destNode = writable(undefined);
const numRoutes = writable(1);
const searchDuration = writable(undefined);
const selectedDate = writable(undefined);
const tracerouteQueryResults = writable(undefined);

const maxRoutes = writable(2);

const backendBaseURL = readable("http://localhost:8100");

export {srcNode, destNode, numRoutes, searchDuration, selectedDate, backendBaseURL, tracerouteQueryResults, maxRoutes};
