(function () {

    const chart = c3.generate({
        data: {
            columns: [],
            type : 'donut',
            onclick: function (d, i) { console.log("onclick", d, i); },
            onmouseover: function (d, i) { console.log("onmouseover", d, i); },
            onmouseout: function (d, i) { console.log("onmouseout", d, i); }
        },
        donut: {
            title: "Data usage"
        }
    });

    function loadChart(data) {

        const dataBundles = data.usage.data.attributes.plan.bundles.filter((bundle) => bundle.name.includes("Data"));
        if (!dataBundles) {
            console.warn("No data bundles found in ", data);
            return;
        }
        const dataBundle = dataBundles[0],
            used = parseInt(dataBundle.used.value, 10),
            limit = parseInt(dataBundle.limit.value, 10),
            unused = limit - used,
            usedGB = parseFloat(used / 1024 / 1024).toFixed(2),
            unusedGB = parseFloat(unused / 1024 / 1024).toFixed(2),
            usedLabel = `${usedGB} GB used`,
            unusedLabel = `${unusedGB} GB left`;


        chart.load({
            columns: [
                [usedLabel, used],
                [unusedLabel, unused],
            ]
        });
    }


    // Get data
    fetch('/api/')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            loadChart(data);
        });

})();
