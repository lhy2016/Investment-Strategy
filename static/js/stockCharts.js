function createChart(name, type, items) {
    var parsed = JSON.parse(items)
    let price = [];
    let stock_date = [];
    if (typeof(parsed["suggestion"]) !== undefined){
        parsed["suggestion"][type]['history'][name].forEach((point) => {
            // create label
            stock_date.push(point[0]);
            // create data
            price.push(point[1]);
        });
    }
    let data = {
        labels: "",
        datasets: [{
            label: stock_date,
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: price,
        }]
    }

    let config = {
        type: 'line',
        data,
        options: {}
    }
    console.log(config);
    new Chart(
        document.getElementById(name),
        config
    );
}