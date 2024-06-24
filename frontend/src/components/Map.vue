<script setup>
import "leaflet/dist/leaflet.css";
import { ref, watchEffect, onMounted } from "vue";
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet";
import L from "leaflet";

const map = ref(null);
const zoom = ref(16);

const start = ref([40.75326495039258, -74.00637797812827]);
const end = ref([40.74486127697681, -73.98732643968263]);

const shadow_id = ref(null);

const midpoint = [
  (start.value[0] + end.value[0]) / 2,
  (start.value[1] + end.value[1]) / 2,
];

async function getShadows(area_id, date) {
  let response = await (
    await fetch(`/api/get_shadows?area_id=${area_id}&time=${date}`)
  ).json();

  for (let shadow of response.shadows) {
    L.polygon(shadow.coords, {
      fillColor: shadow.fill_color,
      fillOpacity: shadow.fill_opacity,
      weight: 0,
    }).addTo(map.value.leafletObject);
  }

  shadow_id.value = response.id;
}

async function prepareArea() {
  let response = await (
    await fetch(
      `/api/prepare_area?startlat=${start.value[0]}&startlon=${start.value[1]}&endlat=${end.value[0]}&endlon=${end.value[1]}`
    )
  ).json();

  for (let building of response.buildings) {
    L.polygon(building.coords, {
      fillColor: building.fill_color,
      fillOpacity: building.fill_opacity,
      weight: 0,
    }).addTo(map.value.leafletObject);
  }

  getShadows(response.id, Date.now());
}

const normal_route = ref(null);
const shadow_route = ref(null);

watchEffect(async () => {
  if (shadow_id.value === null) return;

  let response = await (
    await fetch(
      `/api/route?shadow_id=${shadow_id.value}&startlat=${start.value[0]}&startlon=${start.value[1]}&endlat=${end.value[0]}&endlon=${end.value[1]}`
    )
  ).json();

  console.log(response);

  if (normal_route.value !== null && shadow_route.value !== null) {
    normal_route.value.removeFrom(map.value.leafletObject);
    shadow_route.value.removeFrom(map.value.leafletObject);
  }

  normal_route.value = L.polyline(response.normal_route.coords, {
    color: response.normal_route.color,
    opacity: response.normal_route.opacity,
  }).addTo(map.value.leafletObject);

  shadow_route.value = L.polyline(response.shadow_route.coords, {
    color: response.shadow_route.color,
    opacity: response.shadow_route.opacity,
  }).addTo(map.value.leafletObject);
});
</script>

<template>
  <div>
    <LMap v-model:zoom="zoom" :center="midpoint" ref="map" @ready="prepareArea">
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      />

      <LMarker
        :lat-lng="start"
        @update:lat-lng="(v) => (start = [v.lat, v.lng])"
        draggable
      ></LMarker>
      <LMarker
        :lat-lng="end"
        @update:lat-lng="(v) => (end = [v.lat, v.lng])"
        draggable
      ></LMarker>
    </LMap>
  </div>
</template>
