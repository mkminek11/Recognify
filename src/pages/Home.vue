<template>
    <h1>Domů</h1>
    <div>
        <a :href="`/set/${set.id}`" v-for="set in sets" :key="set.id">{{ set.name }}</a>
    </div>
</template>

<script>
export default {
    name: 'HomePage',
    data() {
        return {
            sets: []
        }
    },
    mounted() {
        this.fetchSets();
    },
    methods: {
        async fetchSets() {
            const response = await fetch('/api/sets');
            this.sets = await response.json();
        }
    }
}
</script>
