function showPackage(ecosystem, name, version) {
    setContent('package');
    packageView(ecosystem, name, version);
}


function packageView(ecosystem, name, version) {

}

function addPackageVersionEntry(ecosystem, name, version) {
    table_body = $("#tableResults>tbody:last-child");
    table_body.append(
        "<tr><td>" +
        ecosystem +
        "</td><td>" +
        name +
        "</td><td>" +
        '<a href="#" onclick="showPackage(\'' + ecosystem + '\', \'' +
                                          name + '\', \'' +
                                          version + '\')">' +
                                          version +
        '</a>' +
        "</td></tr>"
    );
}

function packageSearch() {
    name = $("#packageSearchName").val();
    ecosystem  = $("#packageSearchEcosystem").val();
    table_body = $("#tableResults>tbody").empty();

    fetch("/api/v1/package/" + ecosystem + "/" + name, {
            credentials: "same-origin",
            method: "GET"
    }).then(function(response) {
        if (response.status == 200) {
            response.json().then(function(data) {
                ecosystem = data['ecosystem'];
                name = data['name'];
                for (i = 0; i < data['versions'].length; i++)
                    addPackageVersionEntry(ecosystem, name, data['versions'][i]);
            });
        } else {
            console.log(response);
        }
    });
}

function onBrowseReady() {
    $("#packageSearchSubmit").click(function() { $("#packageSearch").submit(); });
    $("#packageSearch").submit(packageSearch);
}

$(document).ready(onBrowseReady);
