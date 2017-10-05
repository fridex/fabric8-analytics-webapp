function requestAnalyses() {
    if ($("#requestAnalysesType").val() == "package") {
        // TODO: construct URL and report success
        fetch("/api/v1/package", {
                credentials: "same-origin",
                method: "POST"
        }).then(function(response) {
            console.log(response);
            response.json().then(function(data) {
                console.log(data);
            });
        });
    } else {
        // TODO: construct URL and report success
        fetch("/api/v1/project", {
                credentials: "same-origin",
                method: "POST"
        }).then(function(response) {
            console.log(response);
            response.json().then(function(data) {
                console.log(data);
            });
        });
    }

    // ..and close modal
    $("[data-dismiss=modal]").trigger({ type: "click" });
}


function requestAnalysesType() {
    console.log("Request analyses type...");
    if ($("#requestAnalysesType").val() == "project") {
        $("#requestAnalysesUrlDiv").removeClass("hidden");
        $("#requestAnalysesVersionDiv").addClass("hidden");
    } else {
        $("#requestAnalysesUrlDiv").addClass("hidden");
        $("#requestAnalysesVersionDiv").removeClass("hidden");
    }

}


function setLogin() {
    fetch("/api/v1/authorized", {
            credentials: "same-origin",
            method: "GET"
    }).then(function(response) {
        if (response.status == 200) {
            response.json().then(function(data) {
                $("#login-text").text(data["login"]);
                $("#login").addClass("hidden");
                $("#logout").removeClass("hidden")
            });
        } else {
            $("#login-text").text("Anonymous");
            $("#login").removeClass("hidden");
            $("#logout").addClass("hidden")
        }
    });
}


function logOut() {
    fetch("/api/v1/logout", {
            credentials: "same-origin",
            method: "PUT"
    }).then(function(response) {
        if (response.status == 201) {
            setLogin();
        } else {
            console.log("Failed to log out, status code %d", response.status);
        }
    });
}


function logIn() {
    // TODO: introduce endpoint that would redirect to UI
    window.location.replace("/api/v1/generate-token");
}

function setContent(page) {
    fetch("/static/html/" + page, {
            credentials: "same-origin",
            method: "GET"
    }).then(function(response) {
        if (response.status == 200) {
            response.blob().then(function(data) {
                var reader = new FileReader();
                reader.onload = function(event) {
                    $("#content").empty();
                    $("#content").append(reader.result);
                };
                reader.readAsText(data);
            });
        } else {
            console.log("Failed get page '%s'", page);
        }
    });
}

function menuClick(page, item) {
    $("#menuMain>li.active").toggleClass("active", false);
    item.addClass("active");
    setContent(page);
};


function handleMenus() {
    $("#menuBrowse").click(function() { menuClick('browse', $("#menuBrowse")); });
    $("#menuContact").click(function() { menuClick('contact', $("#menuContact")); });
    $("#menuHelp").click(function() { menuClick('help', $("#menuHelp")); });
    $("#menuAbout").click(function() { menuClick('about', $("#menuAbout")); });
    $("#dropdownHelp").click(function() { menuClick('help', $("#dropdownHelp")); });
    $("#dropdownAbout").click(function() { menuClick('about', $("#dropdownAbout")); });
}


function onReady() {
    setLogin();

    $("#logout").click(logOut);
    $("#login").click(logIn);
    $("#requestAnalyses").click(requestAnalyses);
    $("#requestAnalysesType").change(requestAnalysesType);
    handleMenus();
}


$(document).ready(onReady);
