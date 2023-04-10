new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        stockSymbol: '',
        selectedStrategy: '',
        fastPeriod: 10,
        slowPeriod: 30
    },
    methods: {
        submitForm: function () {
            const formData = {
                stock_symbol: this.stockSymbol,
                selected_strategy: this.selectedStrategy,
                fast_period: this.fastPeriod,
                slow_period: this.slowPeriod
            };

            const queryString = new URLSearchParams(formData).toString();
            window.location.href = '/result?' + queryString;
        }
    }
});
