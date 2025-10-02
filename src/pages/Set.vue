<template>
    <h1>{{ set.name }}</h1>
</template>

<script>
export default {
    name: 'SetPage',
    data() {
        return {
            set: {}
        }
    },
    mounted() {
        this.fetchSet();
    },
    methods: {
        async fetchSet() {
            const response = await fetch(`/api/sets/${this.$route.params.id}`);
            this.set = await response.json();
        }
    }
}
</script>
