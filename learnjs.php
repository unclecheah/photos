<html>
    <head>
        <title>CD Choir</title>
        <!-- <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
        <link rel="stylesheet" href="css/unclecheah.css" />
        <link rel="stylesheet" href="css/choir.css" />
        <link rel="stylesheet" href="css/fontawesome.min.css" />
        <script src="https://code.jquery.com/jquery-3.6.3.min.js"></script>
        <script src="https://code.jquery.com/ui/1.13.2/jquery-ui.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js" integrity="sha384-cuYeSxntonz0PPNlHhBs68uyIAVpIIOZZ5JqeqvYYIcEL727kskC66kF92t6Xl2V" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/gasparesganga-jquery-loading-overlay@2.1.7/dist/loadingoverlay.min.js"></script>
        <script src="js/auth.js"></script>
        <script src="js/data.js"></script>
        <script src="js/edit.js"></script> -->

        <script>
            url = "data.php?test";
            // url = "https://api.weather.gov/gridpoints/OKX/35,35/forecast";

            function getPromise () {
                return new Promise (function (resolve, reject) {
                    setTimeout (() => {
                        resolve ('Sunny');
                        // reject ('Rainy');
                    }, 100);
                });
            }

            //  call getPromise async/await
            async function callGP () {
                r = await getPromise ()
                console.log ("getPromise async : " + r)
            };

            async function fetchData () {
                r = await fetch (url);
                data = await r.json();
                console.log (data);
            };

            function main () {
                document.write ("yeah");

                //  1. getPromise
                promise = getPromise ();
                promise.then (
                    function (data) {console.log ("Resolve: " + data);},        //  resolve
                    function (data) {console.log ("Reject: " + data);}          //  reject
                );

                callGP ();          //  2. async getPromise
                fetchData ();       //  3. async fetch
            };

            window.onload = main;
        </script>
    </head>

    <body>
    </body>
</html>
