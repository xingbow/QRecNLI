// /* global d3 $ */
export default {
    name: 'Settings',
    components: {
    },
    props: {
    },
    data() {
        return {
            containerId: 'settingsContainer',
            audioData: {},
            interval: 5,
            sliding: 1
        }
    },
    watch: {
    },
    mounted: function () {
        console.log("this is settings view")
    }
}
