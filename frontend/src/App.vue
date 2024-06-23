<template>
  <section class="w-96">
    <!-- row 1 -->
    <div class="flex flex-row mb-4">
      <div class="flex-1">
          <input
            type="text"
            class="p-4 h-12 mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Start longitude & latitude (comma separated)"
            v-model="startLongitude">
      </div>
    </div>

    <!-- row 2 -->
    <div class="flex flex-row mb-4">
      <div class="flex-1">
          <input
            type="text"
            class="p-4 h-12 mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
            placeholder="End longitude & latitude (comma separated)"
            v-model="endLongitude">
      </div>
    </div>

    <!-- button -->
    <div class="flex flex-row">
      <a 
        :href="'/api/test_augment?start=' + startLongitude + '&end=' + endLongitude"
        target="_blank">
        <button 
          class="w-full py-2 px-4 bg-blue-500 text-white rounded-md shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Search!
        </button>
      </a>
    </div>
  </section>
</template>

<script setup>

import { ref, watch } from 'vue'

const startLongitude = ref('40.7478495,-73.9843726')
const endLongitude = ref('40.7466991,-73.9809522')
</script>
