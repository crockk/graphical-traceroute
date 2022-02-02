import { writable } from 'svelte/store'

const srcNode = writable(undefined);
const destNode = writable(undefined);
const numRoutes = writable(1);
const searchDuration = writable(undefined);
const selectedDate = writable(undefined);

export {srcNode, destNode, numRoutes, searchDuration, selectedDate};
