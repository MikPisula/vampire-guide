<script setup>
import "leaflet/dist/leaflet.css";
import { ref, watchEffect, onMounted } from "vue";
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet";
import L from "leaflet";

const map = ref(null);
const zoom = ref(16);

const start = ref([40.748817, -73.985428]);
const end = ref([40.743291339946865, -73.98000681558766]);

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

watchEffect(async () => {

  console.log(start.value)

  let response = await (
    await fetch(
      `/api/route?shadow_id=${shadow_id.value}&startlat=${start.value[0]}&startlon=${start.value[1]}&endlat=${end.value[0]}&endlon=${end.value[1]}`
    )
  ).json();

  console.log(response);
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
